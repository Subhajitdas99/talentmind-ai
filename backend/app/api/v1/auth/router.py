from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.dependencies import get_auth_service, get_current_user, require_role
from app.api.v1.auth.models import User
from app.api.v1.auth.schemas import LoginRequest, RegisterRequest, TokenPair, UserOut
from app.database.session import get_db_session

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=TokenPair)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenPair:
    service = await get_auth_service(session)
    return await service.register(payload.email, payload.password, payload.full_name)


@auth_router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenPair:
    service = await get_auth_service(session)
    tokens = await service.authenticate(payload.email, payload.password)
    if tokens is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return tokens


@auth_router.get("/me", response_model=UserOut)
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, role=user.role)


@auth_router.get("/admin")
async def admin_only(
    user: Annotated[User, Depends(require_role("admin"))],
) -> dict[str, str]:
    return {"message": f"Hello {user.full_name}"}
