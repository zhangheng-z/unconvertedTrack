from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Child, Content, ContentEvent, User, UserTag
from app.repositories.ai import AiRepository
from app.repositories.contents import ContentRepository
from app.schemas.admin import (
    AiModelCallLogDetail,
    AiModelCallLogListItem,
    AiTopicSuggestionResponse,
    AdminUserProfileResponse,
    ContentAdminResponse,
    ContentCreateRequest,
    ContentUpdateRequest,
    DashboardOverview,
    PreferenceItem,
    PreferenceOverview,
)
from app.utils.time import now


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.contents = ContentRepository(db)
        self.ai = AiRepository(db)

    def create_content(self, payload: ContentCreateRequest) -> ContentAdminResponse:
        data = payload.model_dump(exclude={"tags"})
        data["unlock_type"] = self._normalize_unlock_type(data.get("unlock_type"))
        data["unlock_threshold"] = self._normalize_unlock_threshold(data["unlock_type"], data.get("unlock_threshold"))
        content = self.contents.create(data, payload.tags)
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

    def user_profiles(self, start_date: date | None = None, end_date: date | None = None) -> list[AdminUserProfileResponse]:
        start_at, end_at = self._date_range(start_date, end_date)
        users = list(self.db.scalars(select(User).order_by(desc(User.created_at))))
        if not users:
            return []

        user_ids = [user.id for user in users]
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
        return sorted(rows, key=lambda row: (row.intent_score, row.last_active_at or row.registered_at), reverse=True)

    def update_content(self, content_id: int, payload: ContentUpdateRequest) -> ContentAdminResponse:
        content = self._require_content(content_id)
        data = payload.model_dump(exclude={"tags"}, exclude_unset=True)
        if "unlock_type" in data:
            data["unlock_type"] = self._normalize_unlock_type(data.get("unlock_type"))
        if "unlock_type" in data or "unlock_threshold" in data:
            unlock_type = data.get("unlock_type", content.unlock_type)
            data["unlock_threshold"] = self._normalize_unlock_threshold(unlock_type, data.get("unlock_threshold", content.unlock_threshold))
        content = self.contents.update(content, data, payload.tags if "tags" in payload.model_fields_set else None)
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

    def dashboard(self, start_date: date | None = None, end_date: date | None = None) -> DashboardOverview:
        start_at, end_at = self._date_range(start_date, end_date)
        user_stmt = select(func.count(User.id)).where(User.created_at >= start_at)
        if end_at is not None:
            user_stmt = user_stmt.where(User.created_at < end_at)
        new_users = self.db.scalar(user_stmt) or 0
        return DashboardOverview(
            new_users=new_users,
            active_users=self.contents.active_user_count(start_at, end_at),
            claimed=self.contents.event_count("claim", start_at, end_at),
            downloaded=self.contents.event_count("download", start_at, end_at),
            shared=self.contents.event_count("share", start_at, end_at),
            leads=self.contents.event_count("lead", start_at, end_at),
        )

    def preferences(self, start_date: date | None = None, end_date: date | None = None) -> PreferenceOverview:
        start_at, end_at = self._date_range(start_date, end_date, get_settings().ai_topic_window_days)
        return PreferenceOverview(
            ages=self._items(self.contents.age_counts(start_at, end_at)),
            subjects=self._items(self.contents.preference_counts(Content.subject, start_at, end_at)),
            problems=self._items(self.contents.preference_counts(Content.problem, start_at, end_at)),
            content_types=self._items(self.contents.preference_counts(Content.content_type, start_at, end_at)),
        )

    def topic_suggestions(self) -> list[AiTopicSuggestionResponse]:
        existing = self.ai.list_recent()
        if not existing:
            self.generate_topic_suggestions()
            existing = self.ai.list_recent()
        return [AiTopicSuggestionResponse.model_validate(item) for item in existing]

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
        top_subject = overview.subjects[0].key if overview.subjects else "语文"
        top_problem = overview.problems[0].key if overview.problems else "学习习惯"
        top_age = overview.ages[0].key if overview.ages else "5-8"
        top_type = overview.content_types[0].key if overview.content_types else "pdf"
        title = f"{top_age}岁{top_subject}{top_problem}7天提升计划"
        target = f"{top_age}岁关注{top_problem}的家长"
        reason = "基于近7天用户筛选、点击、领取、下载和分享行为生成，优先覆盖当前最高频需求。"
        self.ai.create_suggestion(title, target, top_type, reason, metrics)
        self.db.commit()

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
            share_count=metrics.get("share_count", 0),
            lead_count=metrics.get("lead_count", 0),
        )

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
