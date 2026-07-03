from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import now


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    content_type: Mapped[str] = mapped_column(String(40), index=True)
    subject: Mapped[str | None] = mapped_column(String(40), index=True)
    problem: Mapped[str | None] = mapped_column(String(80), index=True)
    target_age_min: Mapped[int | None] = mapped_column(Integer, index=True)
    target_age_max: Mapped[int | None] = mapped_column(Integer, index=True)
    grade: Mapped[str | None] = mapped_column(String(40), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(500))
    file_path: Mapped[str | None] = mapped_column(String(500))
    next_action: Mapped[str | None] = mapped_column(String(80))
    next_action_url: Mapped[str | None] = mapped_column(String(500))
    unlock_type: Mapped[str] = mapped_column(String(40), default="free", index=True)
    unlock_threshold: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    project_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    tags: Mapped[list["ContentTag"]] = relationship(back_populates="content", cascade="all, delete-orphan", order_by="ContentTag.id")


class ContentTag(Base):
    __tablename__ = "content_tags"
    __table_args__ = (UniqueConstraint("content_id", "tag_type", "tag_value", name="uq_content_tag"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), index=True)
    tag_type: Mapped[str] = mapped_column(String(40), index=True)
    tag_value: Mapped[str] = mapped_column(String(80), index=True)

    content: Mapped[Content] = relationship(back_populates="tags")


class ContentEvent(Base):
    __tablename__ = "content_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    child_id: Mapped[int | None] = mapped_column(ForeignKey("children.id"), index=True)
    content_id: Mapped[int | None] = mapped_column(ForeignKey("contents.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    source_channel: Mapped[str | None] = mapped_column(String(80))
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    project_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class UserContentAsset(Base):
    __tablename__ = "user_content_assets"
    __table_args__ = (UniqueConstraint("user_id", "content_id", name="uq_user_content_asset"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), index=True)
    unlocked: Mapped[bool] = mapped_column(Boolean, default=True)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class InviteRecord(Base):
    __tablename__ = "invite_records"
    __table_args__ = (UniqueConstraint("inviter_user_id", "invitee_user_id", name="uq_invite_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    inviter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    invitee_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_content_id: Mapped[int | None] = mapped_column(ForeignKey("contents.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    project_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, default=now)
