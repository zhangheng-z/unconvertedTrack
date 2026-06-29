from datetime import datetime, timedelta

from sqlalchemy import and_, delete, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models import Content, ContentEvent, ContentTag, InviteRecord, UserContentAsset
from app.utils.time import now


class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, content_id: int) -> Content | None:
        return self.db.get(Content, content_id)

    def list_all(self, is_published: bool | None = None) -> list[Content]:
        stmt = select(Content).order_by(desc(Content.updated_at))
        if is_published is not None:
            stmt = stmt.where(Content.is_published.is_(is_published))
        return list(self.db.scalars(stmt))

    def list_published(
        self,
        age: int | None = None,
        grade: str | None = None,
        subject: str | None = None,
        problem: str | None = None,
        content_type: str | None = None,
        sort: str = "smart",
    ) -> list[Content]:
        stmt = select(Content).where(Content.is_published.is_(True))
        if age is not None:
            stmt = stmt.where(
                and_(
                    or_(Content.target_age_min.is_(None), Content.target_age_min <= age),
                    or_(Content.target_age_max.is_(None), Content.target_age_max >= age),
                )
            )
        if grade:
            stmt = stmt.where(or_(Content.grade.is_(None), Content.grade == grade))
        if subject:
            stmt = stmt.where(Content.subject == subject)
        if problem:
            stmt = stmt.where(Content.problem == problem)
        if content_type:
            stmt = stmt.where(Content.content_type == content_type)
        if sort == "latest":
            stmt = stmt.order_by(desc(Content.created_at))
        elif sort == "popular":
            stmt = stmt.outerjoin(ContentEvent).group_by(Content.id).order_by(desc(func.count(ContentEvent.id)))
        else:
            stmt = stmt.order_by(desc(Content.updated_at))
        return list(self.db.scalars(stmt))

    def create(self, data: dict, tags: list[str]) -> Content:
        content = Content(**data)
        self.db.add(content)
        self.db.flush()
        self.replace_tags(content, tags)
        self.db.flush()
        return content

    def update(self, content: Content, data: dict, tags: list[str] | None) -> Content:
        for key, value in data.items():
            if value is not None:
                setattr(content, key, value)
        if tags is not None:
            self.replace_tags(content, tags)
        self.db.flush()
        return content

    def delete(self, content: Content) -> None:
        content_id = content.id
        self.db.execute(delete(ContentEvent).where(ContentEvent.content_id == content_id))
        self.db.execute(delete(UserContentAsset).where(UserContentAsset.content_id == content_id))
        self.db.execute(delete(InviteRecord).where(InviteRecord.source_content_id == content_id))
        self.db.execute(delete(ContentTag).where(ContentTag.content_id == content_id))
        self.db.delete(content)
        self.db.flush()

    def replace_tags(self, content: Content, tags: list[str]) -> None:
        self.db.query(ContentTag).filter(ContentTag.content_id == content.id).delete()
        self.db.add_all(ContentTag(content_id=content.id, tag_type="custom", tag_value=tag) for tag in tags)

    def get_asset(self, user_id: int, content_id: int) -> UserContentAsset | None:
        return self.db.scalar(
            select(UserContentAsset).where(
                UserContentAsset.user_id == user_id,
                UserContentAsset.content_id == content_id,
            )
        )

    def claim_asset(self, user_id: int, content_id: int, unlocked: bool = True) -> UserContentAsset:
        asset = self.get_asset(user_id, content_id)
        if asset is None:
            asset = UserContentAsset(user_id=user_id, content_id=content_id, unlocked=unlocked)
            self.db.add(asset)
            self.db.flush()
        return asset

    def assets_for_contents(self, user_id: int, content_ids: list[int]) -> dict[int, UserContentAsset]:
        if not content_ids:
            return {}
        stmt = select(UserContentAsset).where(
            UserContentAsset.user_id == user_id,
            UserContentAsset.content_id.in_(content_ids),
        )
        return {asset.content_id: asset for asset in self.db.scalars(stmt)}

    def record_event(
        self,
        event_type: str,
        user_id: int | None,
        child_id: int | None = None,
        content_id: int | None = None,
        source_channel: str | None = None,
        properties: dict | None = None,
    ) -> ContentEvent:
        event = ContentEvent(
            user_id=user_id,
            child_id=child_id,
            content_id=content_id,
            event_type=event_type,
            source_channel=source_channel,
            properties=properties or {},
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_assets(self, user_id: int) -> list[tuple[UserContentAsset, Content]]:
        stmt = (
            select(UserContentAsset, Content)
            .join(Content, Content.id == UserContentAsset.content_id)
            .where(UserContentAsset.user_id == user_id)
            .order_by(desc(UserContentAsset.updated_at))
        )
        return list(self.db.execute(stmt).all())

    def content_metrics(
        self,
        content_ids: list[int],
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> dict[int, dict[str, int]]:
        if not content_ids:
            return {}
        metrics = {
            content_id: {"claim_count": 0, "share_count": 0, "effective_share_count": 0, "lead_count": 0}
            for content_id in content_ids
        }
        claim_stmt = (
            select(UserContentAsset.content_id, func.count(UserContentAsset.id))
            .where(UserContentAsset.content_id.in_(content_ids))
            .group_by(UserContentAsset.content_id)
        )
        claim_stmt = self._where_between(claim_stmt, UserContentAsset.created_at, start_at, end_at)
        for content_id, count in self.db.execute(claim_stmt).all():
            metrics[content_id]["claim_count"] = count

        share_stmt = (
            select(ContentEvent.content_id, func.count(func.distinct(ContentEvent.user_id)))
            .where(ContentEvent.content_id.in_(content_ids), ContentEvent.event_type == "share")
            .group_by(ContentEvent.content_id)
        )
        share_stmt = self._where_between(share_stmt, ContentEvent.created_at, start_at, end_at)
        for content_id, count in self.db.execute(share_stmt).all():
            if content_id is not None:
                metrics[content_id]["share_count"] = count

        lead_stmt = (
            select(ContentEvent.content_id, func.count(func.distinct(ContentEvent.user_id)))
            .where(ContentEvent.content_id.in_(content_ids), ContentEvent.event_type == "lead")
            .group_by(ContentEvent.content_id)
        )
        lead_stmt = self._where_between(lead_stmt, ContentEvent.created_at, start_at, end_at)
        for content_id, count in self.db.execute(lead_stmt).all():
            if content_id is not None:
                metrics[content_id]["lead_count"] = count

        effective_share_stmt = (
            select(InviteRecord.source_content_id, func.count(func.distinct(InviteRecord.invitee_user_id)))
            .where(
                InviteRecord.source_content_id.in_(content_ids),
                InviteRecord.status == "completed",
            )
            .group_by(InviteRecord.source_content_id)
        )
        effective_share_stmt = self._where_between(effective_share_stmt, InviteRecord.completed_at, start_at, end_at)
        for content_id, count in self.db.execute(effective_share_stmt).all():
            if content_id is not None:
                metrics[content_id]["effective_share_count"] = count

        return metrics

    def completed_invite_count(self, inviter_user_id: int) -> int:
        return self.db.scalar(
            select(func.count(InviteRecord.id)).where(
                InviteRecord.inviter_user_id == inviter_user_id,
                InviteRecord.status == "completed",
            )
        ) or 0

    def complete_invite(self, inviter_user_id: int, invitee_user_id: int, source_content_id: int | None) -> bool:
        existing = self.db.scalar(
            select(InviteRecord).where(
                InviteRecord.inviter_user_id == inviter_user_id,
                InviteRecord.invitee_user_id == invitee_user_id,
            )
        )
        if existing is not None:
            return False
        self.db.add(
            InviteRecord(
                inviter_user_id=inviter_user_id,
                invitee_user_id=invitee_user_id,
                source_content_id=source_content_id,
                status="completed",
                completed_at=now(),
            )
        )
        self.db.flush()
        return True

    def locked_invite_asset_count(self, user_id: int, invited_count: int = 0) -> int:
        stmt = (
            select(func.count(UserContentAsset.id))
            .join(Content, Content.id == UserContentAsset.content_id)
            .where(
                UserContentAsset.user_id == user_id,
                UserContentAsset.unlocked.is_(False),
                Content.unlock_type == "invite",
                Content.unlock_threshold > invited_count,
            )
        )
        return self.db.scalar(stmt) or 0

    def unlock_eligible_invite_assets(self, user_id: int, invited_count: int) -> None:
        stmt = (
            select(UserContentAsset, Content)
            .join(Content, Content.id == UserContentAsset.content_id)
            .where(
                UserContentAsset.user_id == user_id,
                UserContentAsset.unlocked.is_(False),
                Content.unlock_type == "invite",
                Content.unlock_threshold <= invited_count,
            )
        )
        rows = self.db.execute(stmt).all()
        for asset, _content in rows:
            asset.unlocked = True
        if rows:
            self.db.flush()

    def event_count(self, event_type: str, start_at: datetime, end_at: datetime | None = None) -> int:
        stmt = select(func.count(ContentEvent.id)).where(ContentEvent.event_type == event_type)
        stmt = self._where_between(stmt, ContentEvent.created_at, start_at, end_at)
        return self.db.scalar(stmt) or 0

    def active_user_count(self, start_at: datetime, end_at: datetime | None = None) -> int:
        stmt = select(func.count(func.distinct(ContentEvent.user_id)))
        stmt = self._where_between(stmt, ContentEvent.created_at, start_at, end_at)
        return self.db.scalar(stmt) or 0

    def preference_counts(
        self,
        field,
        start_at: datetime,
        end_at: datetime | None = None,
        limit: int = 10,
    ) -> list[tuple[str, int]]:
        stmt = (
            select(field, func.count(ContentEvent.id))
            .join(ContentEvent, ContentEvent.content_id == Content.id)
            .where(field.is_not(None))
            .group_by(field)
            .order_by(desc(func.count(ContentEvent.id)))
            .limit(limit)
        )
        stmt = self._where_between(stmt, ContentEvent.created_at, start_at, end_at)
        return [(str(key), count) for key, count in self.db.execute(stmt).all()]

    def age_counts(self, start_at: datetime, end_at: datetime | None = None, limit: int = 10) -> list[tuple[str, int]]:
        stmt = (
            select(ContentEvent.properties, func.count(ContentEvent.id))
            .group_by(ContentEvent.properties)
            .limit(200)
        )
        stmt = self._where_between(stmt, ContentEvent.created_at, start_at, end_at)
        counts: dict[str, int] = {}
        for props, count in self.db.execute(stmt).all():
            age = (props or {}).get("age")
            if age is not None:
                counts[str(age)] = counts.get(str(age), 0) + count
        return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]

    @staticmethod
    def since_days(days: int) -> datetime:
        return now() - timedelta(days=days)

    @staticmethod
    def _where_between(stmt, column, start_at: datetime | None, end_at: datetime | None):
        if start_at is not None:
            stmt = stmt.where(column >= start_at)
        if end_at is not None:
            stmt = stmt.where(column < end_at)
        return stmt
