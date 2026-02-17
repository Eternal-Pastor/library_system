from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    login: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=6, max_length=200)
    full_name: str = Field(min_length=1, max_length=300)


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
