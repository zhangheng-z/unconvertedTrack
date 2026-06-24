from datetime import datetime

from sqlalchemy.orm import Session

from app.models import UserSession


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        open_id: str,
        session_key: str | None,
        token_jti: str,
        expires_at: datetime,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            open_id=open_id,
            session_key=session_key,
            token_jti=token_jti,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.flush()
        return session
