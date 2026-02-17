from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_books_isbn"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isbn: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    cards: Mapped[List["BookCard"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    copies: Mapped[List["BookCopy"]] = relationship(
        back_populates="book",
        lazy="selectin",
    )

    current_card: Mapped[Optional["BookCurrentCard"]] = relationship(
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BookCard(Base):
    __tablename__ = "book_cards"
    __table_args__ = (
        CheckConstraint("status IN ('draft','pending','published','archived')", name="status"),
        CheckConstraint(
            "publish_year IS NULL OR (publish_year >= 0 AND publish_year <= 3000)",
            name="publish_year_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(Text, nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[Optional[str]] = mapped_column(Text)
    publish_year: Mapped[Optional[int]] = mapped_column(Integer)

    publisher_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publishers.id", ondelete="SET NULL"),
    )

    cover_url: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reject_reason: Mapped[Optional[str]] = mapped_column(Text)

    book: Mapped["Book"] = relationship(back_populates="cards", lazy="selectin")
    publisher: Mapped[Optional["Publisher"]] = relationship(lazy="selectin")

    authors: Mapped[List["Author"]] = relationship(
        secondary="book_card_authors",
        back_populates="book_cards",
        lazy="selectin",
    )
    genres: Mapped[List["Genre"]] = relationship(
        secondary="book_card_genres",
        back_populates="book_cards",
        lazy="selectin",
    )


class BookCardAuthor(Base):
    __tablename__ = "book_card_authors"

    book_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_cards.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authors.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class BookCardGenre(Base):
    __tablename__ = "book_card_genres"

    book_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_cards.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("genres.id", ondelete="RESTRICT"),
        primary_key=True,
    )


class BookCurrentCard(Base):
    __tablename__ = "book_current_card"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )

    published_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_cards.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    book: Mapped["Book"] = relationship(back_populates="current_card", lazy="selectin")
    published_card: Mapped["BookCard"] = relationship(lazy="selectin")


class BookCopy(Base):
    __tablename__ = "book_copies"
    __table_args__ = (
        UniqueConstraint("inventory_code", name="uq_book_copies_inventory_code"),
        CheckConstraint(
            "status IN ('available','reserved','issued','lost','repair','archived')",
            name="status",
        ),
        CheckConstraint("condition IN ('new','good','ok','bad')", name="condition"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="RESTRICT"),
        nullable=False,
    )

    inventory_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
    )

    status: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    acquired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))  # date можно сделать Date
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    book: Mapped["Book"] = relationship(back_populates="copies", lazy="selectin")
    location: Mapped[Optional["Location"]] = relationship(lazy="selectin")
