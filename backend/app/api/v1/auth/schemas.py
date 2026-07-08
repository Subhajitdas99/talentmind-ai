from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
