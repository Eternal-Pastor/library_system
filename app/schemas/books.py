from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# -------- Input --------

class BookCreateRequest(BaseModel):
    isbn: Optional[str] = Field(default=None, max_length=64)


class BookCardDraftCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = Field(default=None, max_length=5000)
    language: Optional[str] = Field(default=None, max_length=30)
    publish_year: Optional[int] = Field(default=None, ge=0, le=3000)

    publisher_id: Optional[uuid.UUID] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)

    author_ids: list[uuid.UUID] = Field(default_factory=list)
    genre_ids: list[uuid.UUID] = Field(default_factory=list)


class BookCardDraftUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = Field(default=None, max_length=5000)
    language: Optional[str] = Field(default=None, max_length=30)
    publish_year: Optional[int] = Field(default=None, ge=0, le=3000)

    publisher_id: Optional[uuid.UUID] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)

    author_ids: Optional[list[uuid.UUID]] = None
    genre_ids: Optional[list[uuid.UUID]] = None


class ModerationReject(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


# -------- Output --------

class BookOut(BaseModel):
    id: uuid.UUID
    isbn: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BookCardOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    status: str

    title: str
    subtitle: Optional[str]
    description: Optional[str]
    language: Optional[str]
    publish_year: Optional[int]
    publisher_id: Optional[uuid.UUID]
    cover_url: Optional[str]

    created_by: uuid.UUID
    created_at: datetime
    reviewed_by: Optional[uuid.UUID]
    reviewed_at: Optional[datetime]
    reject_reason: Optional[str]

    author_ids: list[uuid.UUID] = []
    genre_ids: list[uuid.UUID] = []

    class Config:
        from_attributes = True


class PublishedBookView(BaseModel):
    book: BookOut
    card: BookCardOut
