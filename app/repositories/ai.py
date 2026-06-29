from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import AiModelCallLog, AiTopicSuggestion


class AiRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_recent(self, limit: int = 20) -> list[AiTopicSuggestion]:
        stmt = select(AiTopicSuggestion).order_by(desc(AiTopicSuggestion.created_at)).limit(limit)
        return list(self.db.scalars(stmt))

    def create_suggestion(self, title: str, target_audience: str, content_type: str, reason: str, metrics: dict) -> AiTopicSuggestion:
        suggestion = AiTopicSuggestion(
            title=title,
            target_audience=target_audience,
            content_type=content_type,
            reason=reason,
            source_metrics=metrics,
        )
        self.db.add(suggestion)
        self.db.flush()
        return suggestion

    def create_model_call_log(self, **values) -> AiModelCallLog:
        log = AiModelCallLog(**values)
        self.db.add(log)
        self.db.flush()
        return log

    def list_model_call_logs(
        self,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        request_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AiModelCallLog]:
        stmt = select(AiModelCallLog).order_by(desc(AiModelCallLog.started_at)).limit(limit)
        if start_at is not None:
            stmt = stmt.where(AiModelCallLog.started_at >= start_at)
        if end_at is not None:
            stmt = stmt.where(AiModelCallLog.started_at < end_at)
        if request_id:
            stmt = stmt.where(AiModelCallLog.request_id == request_id)
        if status:
            stmt = stmt.where(AiModelCallLog.status == status)
        return list(self.db.scalars(stmt))

    def get_model_call_log(self, log_id: int) -> AiModelCallLog | None:
        return self.db.get(AiModelCallLog, log_id)
