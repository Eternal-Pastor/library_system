from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserPublic
from app.services.user_service import create_user, get_user_by_login
from app.services.auth_service import authenticate
from app.utils.security import create_access_token
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserPublic:
    existing = get_user_by_login(db, payload.login)
    if existing:
        raise HTTPException(status_code=409, detail="Login already exists")

    user = create_user(db, payload.login, payload.password, payload.full_name)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user=Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)
