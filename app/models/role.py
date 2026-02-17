from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import ForeignKey, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    # фиксированные id: 1=user, 2=staff, 3=admin
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)  # user|staff|admin
    name: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[List["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        primary_key=True,
    )
