from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.api.v1.auth.repository import UserRepository
from app.api.v1.auth.schemas import TokenPair, TokenPayload
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service encapsulating authentication workflows and token issuance."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def _create_token(self, subject: str, role: str, expires_delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    def create_access_token(self, user_id: int, role: str) -> str:
        return self._create_token(str(user_id), role, timedelta(minutes=settings.token_expire_minutes))

    def create_refresh_token(self, user_id: int, role: str) -> str:
        return self._create_token(str(user_id), role, timedelta(days=7))

    async def authenticate(self, email: str, password: str) -> TokenPair | None:
        user = await self._repository.get_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        access_token = self.create_access_token(user.id, user.role)
        refresh_token = self.create_refresh_token(user.id, user.role)
        await self._repository.update_refresh_token(user, refresh_token)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def register(self, email: str, password: str, full_name: str) -> TokenPair:
        hashed_password = self.hash_password(password)
        user = await self._repository.create(email=email, hashed_password=hashed_password, full_name=full_name)
        access_token = self.create_access_token(user.id, user.role)
        refresh_token = self.create_refresh_token(user.id, user.role)
        await self._repository.update_refresh_token(user, refresh_token)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenPair | None:
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        except JWTError:
            return None

        token_payload = TokenPayload(**payload)
        user = await self._repository.get_by_id(int(token_payload.sub))
        if not user or user.refresh_token != refresh_token:
            return None
        access_token = self.create_access_token(user.id, user.role)
        new_refresh_token = self.create_refresh_token(user.id, user.role)
        await self._repository.update_refresh_token(user, new_refresh_token)
        return TokenPair(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, user_id: int) -> None:
        user = await self._repository.get_by_id(user_id)
        if user is not None:
            await self._repository.update_refresh_token(user, None)
