from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.time import now


class AiTopicSuggestion(Base):
    __tablename__ = "ai_topic_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    target_audience: Mapped[str] = mapped_column(String(160))
    content_type: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    source_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    project_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class AiModelCallLog(Base):
    __tablename__ = "ai_model_call_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    task_type: Mapped[str] = mapped_column(String(80), default="unknown", index=True)
    step_name: Mapped[str] = mapped_column(String(120), default="unknown", index=True)
    provider: Mapped[str] = mapped_column(String(80), default="vectorengine")
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(200))
    http_method: Mapped[str] = mapped_column(String(20), default="POST")
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    response_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prompt_text: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    response_text: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="success", index=True)
    error_message: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    image_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
