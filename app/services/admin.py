from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Child, Content, ContentEvent, GradeTag, ProblemCategory, ProblemTag, SubjectTag, TaxonomyTag, User, UserTag
from app.repositories.ai import AiRepository
from app.repositories.contents import ContentRepository
from app.schemas.admin import (
    AiTopicSuggestionUpsertRequest,
    AllowedTopicOptions,
    AiModelCallLogDetail,
    AiModelCallLogListItem,
    AiTopicSuggestionResponse,
    AdminUserPageResponse,
    AdminUserProfileResponse,
    ContentAdminResponse,
    ContentCreateRequest,
    ContentUpdateRequest,
    DashboardOverview,
    PreferenceItem,
    PreferenceOverview,
    TaxonomyOptionsResponse,
    TaxonomyTagCreateRequest,
    TaxonomyTagResponse,
    TaxonomyTagUpdateRequest,
    TopicRecommendationContext,
    TopicRelatedContent,
)
from app.services.llm import LlmContentGenerator, LlmGenerationError
from app.utils.time import now


class AdminService:
    DEFAULT_TAXONOMY = {
        "subject": ["语文", "数学", "英语", "编程"],
        "grade": ["幼小衔接", "一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "小升初"],
        "problem_category": ["语文", "数学", "英语", "习惯", "情绪/适应"],
        "problem": {
            "语文": ["识字少", "拼音不熟", "阅读理解差", "写字慢", "看图写话不会写", "作文没思路", "幼小衔接"],
            "数学": ["计算慢", "计算容易错", "口算薄弱", "应用题不会做", "审题不清", "数感弱"],
            "英语": ["字母不熟", "单词记不住", "自然拼读薄弱", "听力跟不上", "口语不敢说", "阅读看不懂"],
            "习惯": ["作业拖拉", "注意力不集中", "粗心马虎", "坐不住", "依赖家长陪写", "学习主动性差"],
            "情绪/适应": ["畏难情绪", "考试紧张", "抗拒学习", "缺乏自信", "亲子沟通困难", "入学适应慢"],
        },
    }
    TAXONOMY_MODELS = {
        "subject": SubjectTag,
        "grade": GradeTag,
        "problem_category": ProblemCategory,
        "problem": ProblemTag,
    }

    def __init__(self, db: Session):
        self.db = db
        self.contents = ContentRepository(db)
        self.ai = AiRepository(db)
        self._ensure_default_taxonomy()

    def create_content(self, payload: ContentCreateRequest) -> ContentAdminResponse:
        problem_tags = self._normalize_problem_tags(payload.problem_tags, payload.problem)
        data = payload.model_dump(exclude={"tags", "problem_tags"})
        data["problem"] = problem_tags[0] if problem_tags else data.get("problem")
        data["unlock_type"] = self._normalize_unlock_type(data.get("unlock_type"))
        data["unlock_threshold"] = self._normalize_unlock_threshold(data["unlock_type"], data.get("unlock_threshold"))
        content = self.contents.create(data, payload.tags)
        self.contents.replace_tags_by_type(content, "problem", problem_tags)
        self.db.commit()
        return self._content_response(content)

    def list_contents(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        is_published: bool | None = None,
    ) -> list[ContentAdminResponse]:
        start_at, end_at = self._date_range(start_date, end_date)
        contents = self.contents.list_all(is_published)
        metrics = self.contents.content_metrics([content.id for content in contents], start_at, end_at)
        return [self._content_response(content, metrics.get(content.id, {})) for content in contents]

    def user_profiles(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        page: int = 1,
        page_size: int = 5,
    ) -> AdminUserPageResponse:
        start_at, end_at = self._date_range(start_date, end_date)
        page = max(page, 1)
        page_size = min(max(page_size, 1), 50)
        total = self.db.scalar(select(func.count(User.id))) or 0
        users = list(self.db.scalars(
            select(User)
            .order_by(desc(User.created_at), desc(User.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
        ))
        return AdminUserPageResponse(
            items=self._user_profile_rows(users, start_at, end_at),
            total=total,
            page=page,
            page_size=page_size,
            recommended=self._recommended_user_profiles(start_at, end_at, 3),
        )

    def _user_profile_rows(
        self,
        users: list[User],
        start_at: datetime,
        end_at: datetime | None,
    ) -> list[AdminUserProfileResponse]:
        user_ids = [user.id for user in users]
        if not user_ids:
            return []
        children = self._first_children(user_ids)
        tags = self._user_tags(user_ids)
        event_counts = self._user_event_counts(user_ids, start_at, end_at)
        last_active = self._last_active_at(user_ids)

        rows = []
        for user in users:
            counts = event_counts.get(user.id, {})
            claim_count = counts.get("claim", 0)
            download_count = counts.get("download", 0)
            share_count = counts.get("share", 0)
            assessment_count = counts.get("assessment", 0) + counts.get("assessment_complete", 0)
            camp_count = counts.get("camp", 0) + counts.get("camp_signup", 0) + counts.get("training", 0)
            lead_count = counts.get("lead", 0)
            intent_score = (
                claim_count * 3
                + download_count * 4
                + share_count * 5
                + assessment_count * 6
                + camp_count * 8
                + lead_count * 10
            )
            child = children.get(user.id)
            rows.append(
                AdminUserProfileResponse(
                    user_id=user.id,
                    open_id=user.open_id,
                    nickname=user.nickname,
                    avatar_url=user.avatar_url,
                    source_channel=user.source_channel,
                    child_age=child.age if child else None,
                    child_grade=child.grade if child else None,
                    tags=tags.get(user.id, []),
                    registered_at=user.created_at,
                    last_active_at=last_active.get(user.id),
                    claim_count=claim_count,
                    download_count=download_count,
                    share_count=share_count,
                    assessment_count=assessment_count,
                    camp_count=camp_count,
                    lead_count=lead_count,
                    intent_score=intent_score,
                    intent_level=self._intent_level(intent_score),
                    recommended_action=self._recommended_action(
                        claim_count,
                        download_count,
                        share_count,
                        assessment_count,
                        camp_count,
                        lead_count,
                    ),
                )
            )
        return rows

    def _recommended_user_profiles(
        self,
        start_at: datetime,
        end_at: datetime | None,
        limit: int,
    ) -> list[AdminUserProfileResponse]:
        event_types = {"claim", "download", "share", "assessment", "assessment_complete", "camp", "camp_signup", "training", "lead"}
        stmt = (
            select(ContentEvent.user_id, ContentEvent.event_type, func.count(ContentEvent.id))
            .where(
                ContentEvent.user_id.is_not(None),
                ContentEvent.event_type.in_(event_types),
                ContentEvent.created_at >= start_at,
            )
            .group_by(ContentEvent.user_id, ContentEvent.event_type)
        )
        if end_at is not None:
            stmt = stmt.where(ContentEvent.created_at < end_at)
        counts_by_user: dict[int, dict[str, int]] = {}
        for user_id, event_type, count in self.db.execute(stmt).all():
            counts_by_user.setdefault(user_id, {})[event_type] = count
        scored = []
        for user_id, counts in counts_by_user.items():
            claim_count = counts.get("claim", 0)
            download_count = counts.get("download", 0)
            share_count = counts.get("share", 0)
            assessment_count = counts.get("assessment", 0) + counts.get("assessment_complete", 0)
            camp_count = counts.get("camp", 0) + counts.get("camp_signup", 0) + counts.get("training", 0)
            lead_count = counts.get("lead", 0)
            score = (
                claim_count * 3
                + download_count * 4
                + share_count * 5
                + assessment_count * 6
                + camp_count * 8
                + lead_count * 10
            )
            if score > 0:
                scored.append((user_id, score))
        top_ids = [user_id for user_id, _ in sorted(scored, key=lambda item: item[1], reverse=True)[:limit]]
        if not top_ids:
            return []
        users = list(self.db.scalars(select(User).where(User.id.in_(top_ids))))
        user_by_id = {user.id: user for user in users}
        ordered_users = [user_by_id[user_id] for user_id in top_ids if user_id in user_by_id]
        return self._user_profile_rows(ordered_users, start_at, end_at)

    def update_content(self, content_id: int, payload: ContentUpdateRequest) -> ContentAdminResponse:
        content = self._require_content(content_id)
        data = payload.model_dump(exclude={"tags", "problem_tags"}, exclude_unset=True)
        should_update_problem_tags = "problem_tags" in payload.model_fields_set or "problem" in payload.model_fields_set
        if should_update_problem_tags:
            requested_tags = payload.problem_tags if "problem_tags" in payload.model_fields_set else None
            problem_tags = self._normalize_problem_tags(requested_tags, data.get("problem"))
            data["problem"] = problem_tags[0] if problem_tags else data.get("problem")
        if "unlock_type" in data:
            data["unlock_type"] = self._normalize_unlock_type(data.get("unlock_type"))
        if "unlock_type" in data or "unlock_threshold" in data:
            unlock_type = data.get("unlock_type", content.unlock_type)
            data["unlock_threshold"] = self._normalize_unlock_threshold(unlock_type, data.get("unlock_threshold", content.unlock_threshold))
        content = self.contents.update(content, data, payload.tags if "tags" in payload.model_fields_set else None)
        if should_update_problem_tags:
            self.contents.replace_tags_by_type(content, "problem", problem_tags)
        self.db.commit()
        return self._content_response(content)

    def publish_content(self, content_id: int, is_published: bool) -> ContentAdminResponse:
        content = self._require_content(content_id)
        content.is_published = is_published
        self.db.commit()
        self.db.refresh(content)
        return self._content_response(content)

    def delete_content(self, content_id: int) -> None:
        content = self._require_content(content_id)
        self.contents.delete(content)
        self.db.commit()

    def taxonomy_tags(self) -> list[TaxonomyTagResponse]:
        rows: list[TaxonomyTagResponse] = []
        for tag_type in ("subject", "grade", "problem_category", "problem"):
            model = self.TAXONOMY_MODELS[tag_type]
            tags = self.db.scalars(select(model).order_by(model.sort_order, model.id))
            rows.extend(self._taxonomy_response(tag_type, tag) for tag in tags)
        return rows

    def taxonomy_options(self) -> TaxonomyOptionsResponse:
        subject_rows = list(self.db.scalars(self._active_taxonomy_stmt(SubjectTag)))
        grade_rows = list(self.db.scalars(self._active_taxonomy_stmt(GradeTag)))
        category_rows = list(self.db.scalars(self._active_taxonomy_stmt(ProblemCategory)))
        problem_rows = list(self.db.scalars(self._active_taxonomy_stmt(ProblemTag)))
        problem_categories = []
        for category in category_rows:
            problem_categories.append({
                "id": category.id,
                "label": category.label,
                "problems": [problem.label for problem in problem_rows if problem.category_id == category.id],
            })
        return TaxonomyOptionsResponse(
            subjects=[tag.label for tag in subject_rows],
            grades=[tag.label for tag in grade_rows],
            problems=[tag.label for tag in problem_rows],
            problem_categories=problem_categories,
        )

    def create_taxonomy_tag(self, payload: TaxonomyTagCreateRequest) -> TaxonomyTagResponse:
        label = payload.label.strip()
        if not label:
            raise HTTPException(status_code=400, detail="label is required")
        model = self._taxonomy_model(payload.tag_type)
        parent_id = self._normalize_taxonomy_parent(payload.tag_type, payload.parent_id)
        max_order_stmt = select(func.max(model.sort_order))
        if payload.tag_type == "problem":
            max_order_stmt = max_order_stmt.where(ProblemTag.category_id == parent_id)
        max_order = self.db.scalar(
            max_order_stmt
        ) or 0
        tag_data = {"label": label, "is_active": payload.is_active, "sort_order": max_order + 10}
        if payload.tag_type == "problem":
            tag_data["category_id"] = parent_id
        tag = model(**tag_data)
        self.db.add(tag)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="tag already exists") from exc
        self.db.refresh(tag)
        return self._taxonomy_response(payload.tag_type, tag)

    def update_taxonomy_tag(
        self,
        tag_id: int,
        payload: TaxonomyTagUpdateRequest,
        tag_type: str | None = None,
    ) -> TaxonomyTagResponse:
        tag_type, tag = self._require_taxonomy_tag(tag_id, tag_type)
        if tag is None:
            raise HTTPException(status_code=404, detail="taxonomy tag not found")
        if payload.label is not None:
            label = payload.label.strip()
            if not label:
                raise HTTPException(status_code=400, detail="label is required")
            tag.label = label
        if "parent_id" in payload.model_fields_set:
            parent_id = self._normalize_taxonomy_parent(tag_type, payload.parent_id)
            if tag_type == "problem":
                tag.category_id = parent_id
        if payload.is_active is not None:
            tag.is_active = payload.is_active
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="tag already exists") from exc
        self.db.refresh(tag)
        return self._taxonomy_response(tag_type, tag)

    def delete_taxonomy_tag(self, tag_id: int, tag_type: str) -> None:
        tag_type, tag = self._require_taxonomy_tag(tag_id, tag_type)
        if tag_type == "problem_category":
            problems = self.db.scalars(select(ProblemTag).where(ProblemTag.category_id == tag.id)).all()
            for problem in problems:
                self.db.delete(problem)
        self.db.delete(tag)
        self.db.commit()

    def dashboard(self, start_date: date | None = None, end_date: date | None = None) -> DashboardOverview:
        start_at, end_at = self._date_range(start_date, end_date)
        current = self._dashboard_counts(start_at, end_at)
        previous_start_at, previous_end_at = self._previous_date_range(start_at, end_at)
        previous = self._dashboard_counts(previous_start_at, previous_end_at)
        return DashboardOverview(
            **current,
            changes={key: self._metric_change(current[key], previous[key]) for key in current},
        )

    def preferences(self, start_date: date | None = None, end_date: date | None = None) -> PreferenceOverview:
        start_at, end_at = self._date_range(start_date, end_date, get_settings().ai_topic_window_days)
        return PreferenceOverview(
            ages=self._items(self.contents.age_counts(start_at, end_at)),
            subjects=self._items(self.contents.preference_counts(Content.subject, start_at, end_at)),
            problems=self._items(self.contents.problem_preference_counts(start_at, end_at)),
            content_types=self._items(self.contents.preference_counts(Content.content_type, start_at, end_at)),
        )

    def topic_suggestions(self) -> list[AiTopicSuggestionResponse]:
        existing = self._sort_topic_suggestions(self.ai.list_recent())[:4]
        if not existing:
            self.generate_topic_suggestions()
            existing = self._sort_topic_suggestions(self.ai.list_recent())[:4]
        return [AiTopicSuggestionResponse.model_validate(item) for item in existing]

    def create_topic_suggestion(self, payload: AiTopicSuggestionUpsertRequest) -> AiTopicSuggestionResponse:
        data = self._topic_suggestion_payload(payload)
        suggestion = self.ai.create_suggestion(
            data["title"],
            data["target_audience"],
            data["content_type"],
            data["reason"],
            data["source_metrics"],
        )
        self.db.commit()
        self.db.refresh(suggestion)
        return AiTopicSuggestionResponse.model_validate(suggestion)

    def update_topic_suggestion(self, suggestion_id: int, payload: AiTopicSuggestionUpsertRequest) -> AiTopicSuggestionResponse:
        suggestion = self._require_topic_suggestion(suggestion_id)
        data = self._topic_suggestion_payload(payload, suggestion.source_metrics or {})
        suggestion = self.ai.update_suggestion(suggestion, data)
        self.db.commit()
        self.db.refresh(suggestion)
        return AiTopicSuggestionResponse.model_validate(suggestion)

    def delete_topic_suggestion(self, suggestion_id: int) -> None:
        suggestion = self._require_topic_suggestion(suggestion_id)
        self.ai.delete_suggestion(suggestion)
        self.db.commit()

    def topic_recommendation_context(self) -> TopicRecommendationContext:
        start_at, end_at = self._date_range(None, None, get_settings().ai_topic_window_days)
        preferences = self.preferences()
        contents = self.contents.list_all(is_published=True)
        content_ids = [content.id for content in contents]
        metrics = self.contents.content_metrics(content_ids, start_at, end_at)
        event_counts = self.contents.content_event_counts(content_ids, {"download", "share"}, start_at, end_at)
        related_rows = []
        for content in contents:
            content_metrics = metrics.get(content.id, {})
            counts = event_counts.get(content.id, {})
            claim_count = content_metrics.get("claim_count", 0)
            download_count = counts.get("download", 0)
            share_count = counts.get("share", 0)
            related_rows.append(
                TopicRelatedContent(
                    content_id=content.id,
                    title=content.title,
                    subject=content.subject,
                    grade=content.grade,
                    content_type=content.content_type,
                    problem_tags=self._content_problem_tags(content),
                    claim_count=claim_count,
                    download_count=download_count,
                    share_count=share_count,
                    download_rate=self._rate(download_count, claim_count),
                    share_rate=self._rate(share_count, claim_count),
                )
            )
        related_rows.sort(key=lambda item: (item.claim_count + item.download_count * 2 + item.share_count * 2), reverse=True)
        return TopicRecommendationContext(
            preferences=preferences,
            related_contents=related_rows[:12],
            allowed_options=self._allowed_topic_options(),
        )

    def generate_ai_topic_suggestions(self) -> list[AiTopicSuggestionResponse]:
        context = self.topic_recommendation_context().model_dump()
        generator = LlmContentGenerator()
        generator.set_trace_context(task_type="topic_suggestion")
        try:
            result = generator.generate_topic_suggestions(context)
        except LlmGenerationError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        if result is None:
            raise HTTPException(status_code=400, detail="AI topic generation requires VECTORENGINE_API_KEY")
        created_count = 0
        for item in result.suggestions:
            if created_count >= 4:
                break
            try:
                data = self._topic_suggestion_payload(
                    AiTopicSuggestionUpsertRequest(
                        title=item["title"],
                        target_audience=item.get("target_audience") or "小学低年级家长",
                        content_type=item.get("content_type") or "pdf",
                        subject=item.get("subject") or "",
                        grade=item.get("grade") or "",
                        problem_tags=item.get("problem_tags", []),
                        priority=item.get("priority") or "medium",
                        reason=item.get("reason") or "基于热门偏好和内容表现生成。",
                        next_action=item.get("next_action") or "",
                    ),
                    {
                        "generation_source": "llm",
                        "model": result.model,
                        "context": context,
                    },
                )
            except HTTPException:
                continue
            self.ai.create_suggestion(
                data["title"],
                data["target_audience"],
                data["content_type"],
                data["reason"],
                data["source_metrics"],
            )
            created_count += 1
        if created_count == 0:
            raise HTTPException(status_code=502, detail="AI topic generation returned no valid suggestions")
        self.db.commit()
        rows = self._sort_topic_suggestions(self.ai.list_recent())[:4]
        return [AiTopicSuggestionResponse.model_validate(item) for item in rows]

    def list_model_call_logs(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        request_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AiModelCallLogListItem]:
        start_at, end_at = self._date_range(start_date, end_date)
        logs = self.ai.list_model_call_logs(start_at, end_at, request_id, status, min(max(limit, 1), 200))
        return [AiModelCallLogListItem.model_validate(log) for log in logs]

    def model_call_log_detail(self, log_id: int) -> AiModelCallLogDetail:
        log = self.ai.get_model_call_log(log_id)
        if log is None:
            raise HTTPException(status_code=404, detail="model call log not found")
        return AiModelCallLogDetail.model_validate(log)

    def generate_topic_suggestions(self) -> None:
        overview = self.preferences()
        metrics = overview.model_dump()
        allowed = self._allowed_topic_options()
        top_subject = overview.subjects[0].key if overview.subjects else (allowed.subjects[0] if allowed.subjects else "")
        top_problem = overview.problems[0].key if overview.problems else (allowed.problem_tags[0] if allowed.problem_tags else "")
        top_grade = allowed.grades[0] if allowed.grades else ""
        top_age = overview.ages[0].key if overview.ages else "5-8"
        top_type = overview.content_types[0].key if overview.content_types else "pdf"
        title = f"{top_age}岁{top_subject}{top_problem}7天提升计划"
        target = f"{top_age}岁关注{top_problem}的家长"
        reason = "基于近7天用户筛选、点击、领取、下载和分享行为生成，优先覆盖当前最高频需求。"
        data = self._topic_suggestion_payload(
            AiTopicSuggestionUpsertRequest(
                title=title,
                target_audience=target,
                content_type=top_type,
                subject=top_subject,
                grade=top_grade,
                problem_tags=[top_problem] if top_problem else [],
                priority="medium",
                reason=reason,
                next_action="AI内容生成",
            ),
            {"generation_source": "rule", "context": metrics},
        )
        self.ai.create_suggestion(data["title"], data["target_audience"], data["content_type"], data["reason"], data["source_metrics"])
        self.db.commit()

    def _require_topic_suggestion(self, suggestion_id: int):
        suggestion = self.ai.get_suggestion(suggestion_id)
        if suggestion is None:
            raise HTTPException(status_code=404, detail="topic suggestion not found")
        return suggestion

    def _sort_topic_suggestions(self, suggestions: list) -> list:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            suggestions,
            key=lambda item: (
                priority_order.get((item.source_metrics or {}).get("priority"), 3),
                -item.created_at.timestamp(),
            ),
        )

    def _allowed_topic_options(self) -> AllowedTopicOptions:
        options = self.taxonomy_options()
        return AllowedTopicOptions(
            subjects=options.subjects,
            grades=options.grades,
            problem_tags=options.problems,
        )

    def _topic_suggestion_payload(self, payload: AiTopicSuggestionUpsertRequest, base_metrics: dict | None = None) -> dict:
        allowed = self._allowed_topic_options()
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title is required")
        subject = payload.subject.strip()
        grade = payload.grade.strip()
        content_type = payload.content_type.strip() or "pdf"
        problem_tags = [tag.strip() for tag in payload.problem_tags if tag and tag.strip()]
        invalid = []
        if subject not in allowed.subjects:
            invalid.append("subject")
        if grade not in allowed.grades:
            invalid.append("grade")
        if content_type not in allowed.content_types:
            invalid.append("content_type")
        if not problem_tags or any(tag not in allowed.problem_tags for tag in problem_tags):
            invalid.append("problem_tags")
        if invalid:
            raise HTTPException(status_code=400, detail=f"invalid topic fields: {', '.join(invalid)}")
        metrics = dict(base_metrics or {})
        metrics.update({
            "subject": subject,
            "grade": grade,
            "problem_tags": list(dict.fromkeys(problem_tags)),
            "priority": payload.priority.strip() or "medium",
            "next_action": (payload.next_action or "").strip(),
        })
        return {
            "title": title[:160],
            "target_audience": (payload.target_audience or "小学低年级家长").strip()[:160],
            "content_type": content_type,
            "reason": (payload.reason or "基于热门偏好和内容表现生成。").strip(),
            "source_metrics": metrics,
        }

    def _require_content(self, content_id: int) -> Content:
        content = self.contents.get(content_id)
        if content is None:
            raise HTTPException(status_code=404, detail="content not found")
        return content

    def _content_response(self, content: Content, metrics: dict[str, int] | None = None) -> ContentAdminResponse:
        metrics = metrics if metrics is not None else self.contents.content_metrics([content.id]).get(content.id, {})
        return ContentAdminResponse(
            id=content.id,
            title=content.title,
            content_type=content.content_type,
            subject=content.subject,
            problem=content.problem,
            problem_tags=self._content_problem_tags(content),
            target_age_min=content.target_age_min,
            target_age_max=content.target_age_max,
            grade=content.grade,
            summary=content.summary,
            cover_url=content.cover_url,
            file_path=content.file_path,
            next_action=content.next_action,
            next_action_url=content.next_action_url,
            unlock_type=content.unlock_type or "free",
            unlock_threshold=content.unlock_threshold or 0,
            is_published=content.is_published,
            claim_count=metrics.get("claim_count", 0),
            download_count=metrics.get("download_count", 0),
            share_count=metrics.get("share_count", 0),
            lead_count=metrics.get("lead_count", 0),
        )

    @staticmethod
    def _normalize_problem_tags(problem_tags: list[str] | None, fallback_problem: str | None = None) -> list[str]:
        values = list(problem_tags or [])
        if not values and fallback_problem:
            values = [fallback_problem]
        result = []
        seen = set()
        for tag in values:
            value = str(tag or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    @staticmethod
    def _content_problem_tags(content: Content) -> list[str]:
        values = []
        seen = set()
        for tag in content.tags:
            if tag.tag_type != "problem":
                continue
            value = str(tag.tag_value or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            values.append(value)
        if not values and content.problem:
            values.append(content.problem)
        return values

    @staticmethod
    def _items(rows: list[tuple[str, int]]) -> list[PreferenceItem]:
        return [PreferenceItem(key=key, count=count) for key, count in rows]

    @staticmethod
    def _normalize_unlock_type(unlock_type: str | None) -> str:
        return unlock_type if unlock_type in {"free", "invite"} else "free"

    @staticmethod
    def _normalize_unlock_threshold(unlock_type: str, threshold: int | None) -> int:
        if unlock_type == "free":
            return 0
        return max(threshold or 1, 1)

    def _first_children(self, user_ids: list[int]) -> dict[int, Child]:
        rows = self.db.scalars(select(Child).where(Child.user_id.in_(user_ids)).order_by(Child.created_at)).all()
        children: dict[int, Child] = {}
        for child in rows:
            children.setdefault(child.user_id, child)
        return children

    def _user_tags(self, user_ids: list[int]) -> dict[int, list[str]]:
        rows = self.db.execute(
            select(UserTag.user_id, UserTag.tag_value).where(UserTag.user_id.in_(user_ids)).order_by(UserTag.weight.desc())
        ).all()
        tags: dict[int, list[str]] = {}
        for user_id, tag in rows:
            tags.setdefault(user_id, []).append(tag)
        return tags

    def _user_event_counts(
        self,
        user_ids: list[int],
        start_at: datetime,
        end_at: datetime | None,
    ) -> dict[int, dict[str, int]]:
        event_types = {"claim", "download", "share", "assessment", "assessment_complete", "camp", "camp_signup", "training", "lead"}
        stmt = (
            select(ContentEvent.user_id, ContentEvent.event_type, func.count(ContentEvent.id))
            .where(
                ContentEvent.user_id.in_(user_ids),
                ContentEvent.event_type.in_(event_types),
                ContentEvent.created_at >= start_at,
            )
            .group_by(ContentEvent.user_id, ContentEvent.event_type)
        )
        if end_at is not None:
            stmt = stmt.where(ContentEvent.created_at < end_at)
        counts: dict[int, dict[str, int]] = {}
        for user_id, event_type, count in self.db.execute(stmt).all():
            if user_id is not None:
                counts.setdefault(user_id, {})[event_type] = count
        return counts

    def _last_active_at(self, user_ids: list[int]) -> dict[int, datetime]:
        rows = self.db.execute(
            select(ContentEvent.user_id, func.max(ContentEvent.created_at))
            .where(ContentEvent.user_id.in_(user_ids))
            .group_by(ContentEvent.user_id)
        ).all()
        return {user_id: active_at for user_id, active_at in rows if user_id is not None and active_at is not None}

    @staticmethod
    def _intent_level(score: int) -> str:
        if score >= 20:
            return "high"
        if score >= 8:
            return "medium"
        return "low"

    @staticmethod
    def _recommended_action(
        claim_count: int,
        download_count: int,
        share_count: int,
        assessment_count: int,
        camp_count: int,
        lead_count: int,
    ) -> str:
        if lead_count or camp_count:
            return "分配顾问跟进"
        if assessment_count:
            return "推送训练营"
        if download_count or claim_count:
            return "发送进阶资料"
        if share_count:
            return "引导邀请解锁"
        return "发送入门资料"

    def _dashboard_counts(self, start_at: datetime, end_at: datetime | None) -> dict[str, int]:
        user_stmt = select(func.count(User.id)).where(User.created_at >= start_at)
        if end_at is not None:
            user_stmt = user_stmt.where(User.created_at < end_at)
        return {
            "new_users": self.db.scalar(user_stmt) or 0,
            "active_users": 0,
            "claimed": self.contents.event_count("claim", start_at, end_at),
            "downloaded": 0,
            "shared": self.contents.event_count("share", start_at, end_at),
            "leads": self.contents.event_count("lead", start_at, end_at),
        }

    def _ensure_default_taxonomy(self) -> None:
        if self._has_taxonomy_rows():
            self.db.commit()
            return
        self._migrate_legacy_taxonomy()
        if self._has_taxonomy_rows():
            self.db.commit()
            return
        for tag_type in ("subject", "grade"):
            for index, label in enumerate(self.DEFAULT_TAXONOMY[tag_type], start=1):
                self._ensure_simple_taxonomy_tag(self.TAXONOMY_MODELS[tag_type], label, index * 10)
        category_by_label = {}
        for index, label in enumerate(self.DEFAULT_TAXONOMY["problem_category"], start=1):
            category_by_label[label] = self._ensure_simple_taxonomy_tag(ProblemCategory, label, index * 10)
        old_common = self.db.scalar(
            select(TaxonomyTag).where(TaxonomyTag.tag_type == "problem_category", TaxonomyTag.label == "常见")
        )
        if old_common is not None:
            old_common.is_active = False
        seen_problems = set()
        for category_label, problems in self.DEFAULT_TAXONOMY["problem"].items():
            category = category_by_label[category_label]
            for index, label in enumerate(problems, start=1):
                if label in seen_problems:
                    continue
                seen_problems.add(label)
                self._ensure_problem_tag(label, category.id, index * 10)
        self._assign_uncategorized_problems(category_by_label)
        self.db.commit()

    def _has_taxonomy_rows(self) -> bool:
        for model in self.TAXONOMY_MODELS.values():
            if self.db.scalar(select(func.count(model.id))) or 0:
                return True
        return False

    def _ensure_simple_taxonomy_tag(self, model: type[SubjectTag] | type[GradeTag] | type[ProblemCategory], label: str, sort_order: int):
        tag = self.db.scalar(select(model).where(model.label == label))
        if tag is None:
            tag = model(label=label, sort_order=sort_order)
            self.db.add(tag)
            self.db.flush()
        return tag

    def _ensure_problem_tag(self, label: str, category_id: int, sort_order: int) -> ProblemTag:
        tag = self.db.scalar(select(ProblemTag).where(ProblemTag.label == label))
        if tag is None:
            tag = ProblemTag(label=label, category_id=category_id, sort_order=sort_order)
            self.db.add(tag)
            self.db.flush()
        return tag

    def _assign_uncategorized_problems(self, category_by_label: dict[str, ProblemCategory]) -> None:
        problem_to_category = {
            problem: category
            for category, problems in self.DEFAULT_TAXONOMY["problem"].items()
            for problem in problems
        }
        fallback = category_by_label.get("语文") or next(iter(category_by_label.values()), None)
        active_category_ids = {category.id for category in category_by_label.values()}
        rows = self.db.scalars(select(ProblemTag))
        for tag in rows:
            if tag.category_id in active_category_ids:
                continue
            category = category_by_label.get(problem_to_category.get(tag.label, ""), fallback)
            if category is not None:
                tag.category_id = category.id

    def _migrate_legacy_taxonomy(self) -> None:
        legacy_rows = list(self.db.scalars(select(TaxonomyTag).order_by(TaxonomyTag.sort_order, TaxonomyTag.id)))
        if not legacy_rows:
            return
        legacy_categories = {
            row.id: row.label
            for row in legacy_rows
            if row.tag_type == "problem_category"
        }
        category_by_label: dict[str, ProblemCategory] = {}
        for row in legacy_rows:
            if row.tag_type == "subject":
                tag = self._ensure_simple_taxonomy_tag(SubjectTag, row.label, row.sort_order)
            elif row.tag_type == "grade":
                tag = self._ensure_simple_taxonomy_tag(GradeTag, row.label, row.sort_order)
            elif row.tag_type == "problem_category":
                tag = self._ensure_simple_taxonomy_tag(ProblemCategory, row.label, row.sort_order)
                category_by_label[row.label] = tag
            else:
                continue
            tag.is_active = row.is_active

        for row in legacy_rows:
            if row.tag_type != "problem":
                continue
            category_label = legacy_categories.get(row.parent_id)
            category = category_by_label.get(category_label or "")
            if category is None:
                default_category = self._default_problem_category(row.label)
                category = category_by_label.get(default_category)
            if category is None:
                category = self._ensure_simple_taxonomy_tag(ProblemCategory, "常见", 999)
            tag = self._ensure_problem_tag(row.label, category.id, row.sort_order)
            tag.is_active = row.is_active

    def _normalize_taxonomy_parent(self, tag_type: str, parent_id: int | None) -> int | None:
        if tag_type != "problem":
            return None
        if parent_id is None:
            parent_id = self.db.scalar(
                select(ProblemCategory.id)
                .where(ProblemCategory.is_active.is_(True))
                .order_by(ProblemCategory.sort_order, ProblemCategory.id)
            )
        category = self.db.get(ProblemCategory, parent_id) if parent_id is not None else None
        if category is None:
            raise HTTPException(status_code=400, detail="problem category is required")
        return category.id

    @staticmethod
    def _active_taxonomy_stmt(model):
        return select(model).where(model.is_active.is_(True)).order_by(model.sort_order, model.id)

    def _taxonomy_model(self, tag_type: str):
        model = self.TAXONOMY_MODELS.get(tag_type)
        if model is None:
            raise HTTPException(status_code=400, detail="invalid taxonomy type")
        return model

    def _taxonomy_response(self, tag_type: str, tag) -> TaxonomyTagResponse:
        return TaxonomyTagResponse(
            id=tag.id,
            tag_type=tag_type,
            label=tag.label,
            parent_id=tag.category_id if tag_type == "problem" else None,
            is_active=tag.is_active,
            sort_order=tag.sort_order,
        )

    def _require_taxonomy_tag(self, tag_id: int, tag_type: str | None = None):
        if tag_type is not None:
            model = self._taxonomy_model(tag_type)
            tag = self.db.get(model, tag_id)
            if tag is None:
                raise HTTPException(status_code=404, detail="taxonomy tag not found")
            return tag_type, tag

        matches = []
        for current_type, model in self.TAXONOMY_MODELS.items():
            tag = self.db.get(model, tag_id)
            if tag is not None:
                matches.append((current_type, tag))
        if not matches:
            raise HTTPException(status_code=404, detail="taxonomy tag not found")
        if len(matches) > 1:
            raise HTTPException(status_code=400, detail="taxonomy type is required")
        return matches[0]

    def _default_problem_category(self, problem_label: str) -> str:
        for category, problems in self.DEFAULT_TAXONOMY["problem"].items():
            if problem_label in problems:
                return category
        return "语文"

    @staticmethod
    def _previous_date_range(start_at: datetime, end_at: datetime | None) -> tuple[datetime, datetime]:
        current_end_at = end_at or now()
        duration = current_end_at - start_at
        if duration <= timedelta(0):
            duration = timedelta(days=1)
        previous_end_at = start_at
        previous_start_at = previous_end_at - duration
        return previous_start_at, previous_end_at

    @staticmethod
    def _metric_change(current: int, previous: int) -> dict[str, int | float | str]:
        if previous == 0:
            percent = 100.0 if current > 0 else 0.0
        else:
            percent = round(((current - previous) / previous) * 100, 1)
        if current > previous:
            direction = "up"
        elif current < previous:
            direction = "down"
        else:
            direction = "flat"
        return {
            "current": current,
            "previous": previous,
            "percent": percent,
            "direction": direction,
        }

    @staticmethod
    def _rate(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0
        return round(numerator / denominator, 3)

    @staticmethod
    def _date_range(
        start_date: date | None,
        end_date: date | None,
        default_days: int = 7,
    ) -> tuple[datetime, datetime | None]:
        if end_date is not None:
            end_at = datetime.combine(end_date + timedelta(days=1), time.min)
        else:
            end_at = None
        if start_date is not None:
            start_at = datetime.combine(start_date, time.min)
        elif end_date is not None:
            start_at = datetime.combine(end_date - timedelta(days=default_days - 1), time.min)
        else:
            start_at = now() - timedelta(days=default_days)
        return start_at, end_at
