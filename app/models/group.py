from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    grade_level: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    users: Mapped[List["User"]] = relationship(
        secondary="user_groups",
        back_populates="groups",
        lazy="selectin",
    )


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    )
