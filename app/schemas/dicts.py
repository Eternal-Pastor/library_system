from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class AuthorCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=300)
    normalized_name: str | None = Field(default=None, max_length=300)


class AuthorOut(BaseModel):
    id: uuid.UUID
    full_name: str
    normalized_name: str | None

    class Config:
        from_attributes = True


class GenreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class GenreOut(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True


class LocationCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)


class LocationOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True
