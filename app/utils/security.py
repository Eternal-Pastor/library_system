from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_minutes: int | None = None, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp_minutes = expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    expire = now + timedelta(minutes=exp_minutes)

    payload: dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    if extra:
        payload.update(extra)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
