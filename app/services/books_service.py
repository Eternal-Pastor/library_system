from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.book import Book, BookCard, BookCurrentCard
from app.models.author import Author
from app.models.genre import Genre
from app.models.publisher import Publisher


def _load_authors(db: Session, author_ids: list[uuid.UUID]) -> list[Author]:
    if not author_ids:
        return []
    items = db.query(Author).filter(Author.id.in_(author_ids)).all()
    if len(items) != len(set(author_ids)):
        raise ValueError("Some authors not found")
    return items


def _load_genres(db: Session, genre_ids: list[uuid.UUID]) -> list[Genre]:
    if not genre_ids:
        return []
    items = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
    if len(items) != len(set(genre_ids)):
        raise ValueError("Some genres not found")
    return items


def _check_publisher(db: Session, publisher_id: uuid.UUID | None) -> None:
    if publisher_id is None:
        return
    exists = db.query(Publisher.id).filter(Publisher.id == publisher_id).one_or_none()
    if not exists:
        raise ValueError("Publisher not found")


# -------- Books --------

def create_book(db: Session, isbn: str | None = None) -> Book:
    book = Book(isbn=isbn)
    db.add(book)
    db.flush()  # получить id без commit
    return book


# -------- Book cards workflow --------

def create_draft_card(
    db: Session,
    *,
    book_id: uuid.UUID,
    created_by: uuid.UUID,
    title: str,
    subtitle: str | None,
    description: str | None,
    language: str | None,
    publish_year: int | None,
    publisher_id: uuid.UUID | None,
    cover_url: str | None,
    author_ids: list[uuid.UUID],
    genre_ids: list[uuid.UUID],
) -> BookCard:
    _check_publisher(db, publisher_id)
    authors = _load_authors(db, author_ids)
    genres = _load_genres(db, genre_ids)

    card = BookCard(
        book_id=book_id,
        status="draft",
        title=title,
        subtitle=subtitle,
        description=description,
        language=language,
        publish_year=publish_year,
        publisher_id=publisher_id,
        cover_url=cover_url,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    card.authors = authors
    card.genres = genres

    db.add(card)
    db.flush()
    return card


def update_draft_card(
    db: Session,
    *,
    card: BookCard,
    patch: dict,
) -> BookCard:
    if card.status != "draft":
        raise ValueError("Only draft cards can be edited")

    # scalar fields
    for k in ("title", "subtitle", "description", "language", "publish_year", "publisher_id", "cover_url"):
        if k in patch and patch[k] is not None:
            if k == "publisher_id":
                _check_publisher(db, patch[k])
            setattr(card, k, patch[k])

    # allow clearing nullable fields explicitly (если нужно)
    for k in ("subtitle", "description", "language", "publish_year", "publisher_id", "cover_url"):
        if k in patch and patch[k] is None:
            setattr(card, k, None)

    # relations
    if "author_ids" in patch and patch["author_ids"] is not None:
        card.authors = _load_authors(db, patch["author_ids"])

    if "genre_ids" in patch and patch["genre_ids"] is not None:
        card.genres = _load_genres(db, patch["genre_ids"])

    db.flush()
    return card


def submit_card_for_review(db: Session, *, card: BookCard) -> BookCard:
    if card.status != "draft":
        raise ValueError("Only draft cards can be submitted")
    card.status = "pending"
    card.reject_reason = None
    db.flush()
    return card


def publish_card(db: Session, *, card: BookCard, reviewer_id: uuid.UUID) -> BookCard:
    if card.status != "pending":
        raise ValueError("Only pending cards can be published")

    card.status = "published"
    card.reviewed_by = reviewer_id
    card.reviewed_at = datetime.utcnow()
    card.reject_reason = None

    # upsert book_current_card
    current = db.query(BookCurrentCard).filter(BookCurrentCard.book_id == card.book_id).one_or_none()
    if current is None:
        current = BookCurrentCard(
            book_id=card.book_id,
            published_card_id=card.id,
            updated_at=datetime.utcnow(),
        )
        db.add(current)
    else:
        current.published_card_id = card.id
        current.updated_at = datetime.utcnow()

    db.flush()
    return card


def reject_card_to_draft(db: Session, *, card: BookCard, reviewer_id: uuid.UUID, reason: str) -> BookCard:
    if card.status != "pending":
        raise ValueError("Only pending cards can be rejected")

    # статус "rejected" у нас нет (CHECK), поэтому возвращаем в draft + причина
    card.status = "draft"
    card.reviewed_by = reviewer_id
    card.reviewed_at = datetime.utcnow()
    card.reject_reason = reason

    db.flush()
    return card


def get_published_view(db: Session, book_id: uuid.UUID) -> tuple[Book, BookCard] | None:
    book = db.query(Book).filter(Book.id == book_id).one_or_none()
    if not book:
        return None

    current = db.query(BookCurrentCard).filter(BookCurrentCard.book_id == book_id).one_or_none()
    if not current:
        return None

    card = db.query(BookCard).filter(BookCard.id == current.published_card_id).one_or_none()
    if not card or card.status != "published":
        return None

    return book, card
