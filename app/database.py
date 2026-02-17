from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Используем URL object из config.py
SQLALCHEMY_URL = settings.sqlalchemy_url_obj()

engine: Engine = create_engine(
    SQLALCHEMY_URL,
    echo=settings.db_echo,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
