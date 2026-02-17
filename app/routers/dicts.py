from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.rbac import require_roles
from app.models.author import Author
from app.models.genre import Genre
from app.models.location import Location
from app.schemas.dicts import (
    AuthorCreate, AuthorOut,
    GenreCreate, GenreOut,
    LocationCreate, LocationOut,
)

router = APIRouter(prefix="/dicts", tags=["dicts"])


# -------- Authors --------

@router.get("/authors", response_model=list[AuthorOut])
def list_authors(
    q: str | None = Query(default=None, description="Search substring for author name"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AuthorOut]:
    query = db.query(Author)
    if q:
        # пока простой ILIKE; позже заменим на pg_trgm + similarity()
        query = query.filter(Author.full_name.ilike(f"%{q}%"))
    items = query.order_by(Author.full_name.asc()).limit(limit).all()
    return [AuthorOut.model_validate(x) for x in items]


@router.post("/authors", response_model=AuthorOut, status_code=201, dependencies=[Depends(require_roles("staff", "admin"))])
def create_author(payload: AuthorCreate, db: Session = Depends(get_db)) -> AuthorOut:
    author = Author(full_name=payload.full_name, normalized_name=payload.normalized_name)
    db.add(author)
    db.commit()
    db.refresh(author)
    return AuthorOut.model_validate(author)


# -------- Genres --------

@router.get("/genres", response_model=list[GenreOut])
def list_genres(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[GenreOut]:
    items = db.query(Genre).order_by(Genre.name.asc()).limit(limit).all()
    return [GenreOut.model_validate(x) for x in items]


@router.post("/genres", response_model=GenreOut, status_code=201, dependencies=[Depends(require_roles("staff", "admin"))])
def create_genre(payload: GenreCreate, db: Session = Depends(get_db)) -> GenreOut:
    existing = db.query(Genre).filter(Genre.name == payload.name).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Genre already exists")

    genre = Genre(name=payload.name)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return GenreOut.model_validate(genre)


# -------- Locations --------

@router.get("/locations", response_model=list[LocationOut], dependencies=[Depends(require_roles("staff", "admin"))])
def list_locations(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[LocationOut]:
    q = db.query(Location)
    if not include_inactive:
        q = q.filter(Location.is_active.is_(True))
    items = q.order_by(Location.code.asc()).all()
    return [LocationOut.model_validate(x) for x in items]


@router.post("/locations", response_model=LocationOut, status_code=201, dependencies=[Depends(require_roles("staff", "admin"))])
def create_location(payload: LocationCreate, db: Session = Depends(get_db)) -> LocationOut:
    existing = db.query(Location).filter(Location.code == payload.code).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Location code already exists")

    loc = Location(code=payload.code, name=payload.name, description=payload.description, is_active=True)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return LocationOut.model_validate(loc)
