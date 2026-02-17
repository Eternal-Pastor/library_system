from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import hash_password


def get_user_by_login(db: Session, login: str) -> User | None:
    return db.query(User).filter(User.login == login).one_or_none()


def create_user(db: Session, login: str, password: str, full_name: str) -> User:
    user = User(
        login=login,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
