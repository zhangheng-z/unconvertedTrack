from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Content, ContentEvent, User
from app.repositories.ai import AiRepository
from app.repositories.contents import ContentRepository
from app.schemas.admin import (
    AiTopicSuggestionResponse,
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

    def create_content(self, payload: ContentCreateRequest) -> Content:
        data = payload.model_dump(exclude={"tags"})
        content = self.contents.create(data, payload.tags)
        self.db.commit()
        return content

    def list_contents(self) -> list[Content]:
        return self.contents.list_all()

    def update_content(self, content_id: int, payload: ContentUpdateRequest) -> Content:
        content = self._require_content(content_id)
        data = payload.model_dump(exclude={"tags"}, exclude_unset=True)
        content = self.contents.update(content, data, payload.tags if "tags" in payload.model_fields_set else None)
        self.db.commit()
        return content

    def publish_content(self, content_id: int, is_published: bool) -> Content:
        content = self._require_content(content_id)
        content.is_published = is_published
        self.db.commit()
        self.db.refresh(content)
        return content

    def dashboard(self) -> DashboardOverview:
        since = now() - timedelta(days=7)
        new_users = self.db.scalar(select(func.count(User.id)).where(User.created_at >= since)) or 0
        return DashboardOverview(
            new_users=new_users,
            active_users=self.contents.active_user_count(since),
            claimed=self.contents.event_count("claim", since),
            downloaded=self.contents.event_count("download", since),
            shared=self.contents.event_count("share", since),
            leads=self.contents.event_count("lead", since),
        )

    def preferences(self) -> PreferenceOverview:
        since = self.contents.since_days(get_settings().ai_topic_window_days)
        return PreferenceOverview(
            ages=self._items(self.contents.age_counts(since)),
            subjects=self._items(self.contents.preference_counts(Content.subject, since)),
            problems=self._items(self.contents.preference_counts(Content.problem, since)),
            content_types=self._items(self.contents.preference_counts(Content.content_type, since)),
        )

    def topic_suggestions(self) -> list[AiTopicSuggestionResponse]:
        existing = self.ai.list_recent()
        if not existing:
            self.generate_topic_suggestions()
            existing = self.ai.list_recent()
        return [AiTopicSuggestionResponse.model_validate(item) for item in existing]

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

    @staticmethod
    def _items(rows: list[tuple[str, int]]) -> list[PreferenceItem]:
        return [PreferenceItem(key=key, count=count) for key, count in rows]
