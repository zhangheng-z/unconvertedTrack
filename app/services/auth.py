import json
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User
from app.repositories.sessions import SessionRepository
from app.repositories.users import UserRepository
from app.utils.jwt import create_access_token
from app.utils.time import now


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)

    def wechat_login(
        self,
        code: str,
        nickname: str | None = None,
        avatar_url: str | None = None,
    ) -> tuple[User, str, int, bool]:
        settings = get_settings()
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            open_id = f"dev-{code[:48]}"
            user = self.users.get_or_create(
                open_id,
                nickname=nickname,
                avatar_url=avatar_url,
                source_channel="wechat_miniprogram_dev",
            )
            token, jti, expires_in = create_access_token(user.id, open_id)
            self.sessions.create(
                user_id=user.id,
                open_id=open_id,
                session_key=None,
                token_jti=jti,
                expires_at=now() + timedelta(seconds=expires_in),
            )
            self.db.commit()
            return user, token, expires_in, True

        query = urlencode(
            {
                "appid": settings.wechat_app_id,
                "secret": settings.wechat_app_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            }
        )
        url = f"https://api.weixin.qq.com/sns/jscode2session?{query}"
        try:
            with urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"wechat login failed: {exc}") from exc

        open_id = payload.get("openid")
        session_key = payload.get("session_key")
        if not open_id:
            raise HTTPException(status_code=400, detail=payload.get("errmsg", "invalid wechat login response"))

        user = self.users.get_or_create(
            open_id,
            nickname=nickname,
            avatar_url=avatar_url,
            source_channel="wechat_miniprogram",
        )
        token, jti, expires_in = create_access_token(user.id, open_id)
        self.sessions.create(
            user_id=user.id,
            open_id=open_id,
            session_key=session_key,
            token_jti=jti,
            expires_at=now() + timedelta(seconds=expires_in),
        )
        self.db.commit()
        return user, token, expires_in, False
