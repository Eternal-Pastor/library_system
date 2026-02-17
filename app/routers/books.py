from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.book import Book, BookCard
from app.schemas.books import (
    BookCreateRequest,
    BookOut,
    BookCardDraftCreate,
    BookCardDraftUpdate,
    BookCardOut,
    PublishedBookView,
    ModerationReject,
)
from app.services.books_service import (
    create_book,
    create_draft_card,
    update_draft_card,
    submit_card_for_review,
    publish_card,
    reject_card_to_draft,
    get_published_view,
)
from app.models.user import User

router = APIRouter(prefix="/books", tags=["books"])


def _card_to_out(card: BookCard) -> BookCardOut:
    return BookCardOut(
        id=card.id,
        book_id=card.book_id,
        status=card.status,
        title=card.title,
        subtitle=card.subtitle,
        description=card.description,
        language=card.language,
        publish_year=card.publish_year,
        publisher_id=card.publisher_id,
        cover_url=card.cover_url,
        created_by=card.created_by,
        created_at=card.created_at,
        reviewed_by=card.reviewed_by,
        reviewed_at=card.reviewed_at,
        reject_reason=card.reject_reason,
        author_ids=[a.id for a in (card.authors or [])],
        genre_ids=[g.id for g in (card.genres or [])],
    )


# ---------- Public (user) ----------

@router.get("/{book_id}", response_model=PublishedBookView)
def get_published_book(book_id: uuid.UUID, db: Session = Depends(get_db)) -> PublishedBookView:
    res = get_published_view(db, book_id)
    if not res:
        raise HTTPException(status_code=404, detail="Published book not found")
    book, card = res
    return PublishedBookView(book=BookOut.model_validate(book), card=_card_to_out(card))


# ---------- Staff: create book + draft card ----------

@router.post(
    "",
    response_model=PublishedBookView,
    status_code=201,
    dependencies=[Depends(require_roles("staff", "admin"))],
)
def create_book_with_draft(
    book_payload: BookCreateRequest,
    card_payload: BookCardDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PublishedBookView:
    try:
        with db.begin():
            book = create_book(db, isbn=book_payload.isbn)
            card = create_draft_card(
                db,
                book_id=book.id,
                created_by=current_user.id,
                title=card_payload.title,
                subtitle=card_payload.subtitle,
                description=card_payload.description,
                language=card_payload.language,
                publish_year=card_payload.publish_year,
                publisher_id=card_payload.publisher_id,
                cover_url=card_payload.cover_url,
                author_ids=card_payload.author_ids,
                genre_ids=card_payload.genre_ids,
            )
        # draft не публикуется, поэтому PublishedBookView тут условный:
        # возвращаем book + card (draft) тем, кто создал
        return PublishedBookView(book=BookOut.model_validate(book), card=_card_to_out(card))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/cards/{card_id}",
    response_model=BookCardOut,
    dependencies=[Depends(require_roles("staff", "admin"))],
)
def get_card(card_id: uuid.UUID, db: Session = Depends(get_db)) -> BookCardOut:
    card = db.query(BookCard).filter(BookCard.id == card_id).one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return _card_to_out(card)


@router.patch(
    "/cards/{card_id}",
    response_model=BookCardOut,
    dependencies=[Depends(require_roles("staff", "admin"))],
)
def patch_draft_card(
    card_id: uuid.UUID,
    payload: BookCardDraftUpdate,
    db: Session = Depends(get_db),
) -> BookCardOut:
    card = db.query(BookCard).filter(BookCard.id == card_id).one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        with db.begin():
            card = update_draft_card(db, card=card, patch=payload.model_dump(exclude_unset=True))
        return _card_to_out(card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/cards/{card_id}/submit",
    response_model=BookCardOut,
    dependencies=[Depends(require_roles("staff", "admin"))],
)
def submit_card(card_id: uuid.UUID, db: Session = Depends(get_db)) -> BookCardOut:
    card = db.query(BookCard).filter(BookCard.id == card_id).one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        with db.begin():
            card = submit_card_for_review(db, card=card)
        return _card_to_out(card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Admin moderation ----------

@router.post(
    "/cards/{card_id}/publish",
    response_model=BookCardOut,
    dependencies=[Depends(require_roles("admin"))],
)
def publish(card_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> BookCardOut:
    card = db.query(BookCard).filter(BookCard.id == card_id).one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        with db.begin():
            card = publish_card(db, card=card, reviewer_id=current_user.id)
        return _card_to_out(card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/cards/{card_id}/reject",
    response_model=BookCardOut,
    dependencies=[Depends(require_roles("admin"))],
)
def reject(card_id: uuid.UUID, payload: ModerationReject, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> BookCardOut:
    card = db.query(BookCard).filter(BookCard.id == card_id).one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        with db.begin():
            card = reject_card_to_draft(db, card=card, reviewer_id=current_user.id, reason=payload.reason)
        return _card_to_out(card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
