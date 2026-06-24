from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import AiTopicSuggestion


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

