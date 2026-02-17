from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.utils.security import hash_password


def get_user_by_login(db: Session, login: str) -> User | None:
    return db.query(User).filter(User.login == login).one_or_none()


def create_user(db: Session, login: str, password: str, full_name: str) -> User:
    user_role = db.query(Role).filter(Role.code == "user").one()

    user = User(
        login=login,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
        roles=[user_role],
    )
    db.add(user)

    # чтобы сразу получить user.id без commit
    db.flush()
    # refresh не обязателен, но можно оставить — он работает и до commit
    db.refresh(user)

    return user
