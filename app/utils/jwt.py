from datetime import timedelta
from uuid import uuid4

import jwt
from fastapi import HTTPException

from app.config import get_settings
from app.utils.time import now


def create_access_token(user_id: int, open_id: str) -> tuple[str, str, int]:
    settings = get_settings()
    expires_in = settings.jwt_expire_days * 24 * 60 * 60
    expires_at = now() + timedelta(seconds=expires_in)
    jti = uuid4().hex
    payload = {
        "sub": str(user_id),
        "openid": open_id,
        "jti": jti,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    return token, jti, expires_in


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().jwt_secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
