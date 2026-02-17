from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.user_service import get_user_by_login
from app.utils.security import verify_password


def authenticate(db: Session, login: str, password: str) -> User | None:
    user = get_user_by_login(db, login)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
