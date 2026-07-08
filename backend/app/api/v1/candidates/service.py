from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Candidate
from app.api.v1.candidates.repository import CandidateRepository
from app.api.v1.candidates.schemas import CandidateCreate, CandidateUpdate


class CandidateService:
    """Application service for candidate lifecycle operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = CandidateRepository(session)

    async def create(self, payload: CandidateCreate) -> Candidate:
        return await self._repository.create(
            full_name=payload.full_name,
            email=str(payload.email),
            phone=payload.phone,
            current_title=payload.current_title,
            location=payload.location,
            summary=payload.summary,
            years_experience=None,
            status="prospect",
        )

    async def get_by_id(self, candidate_id: str) -> Candidate | None:
        return await self._repository.get_by_id(candidate_id)

    async def list(
        self,
        *,
        page: int,
        size: int,
        query: str | None = None,
        skill: str | None = None,
        location: str | None = None,
    ) -> tuple[list[Candidate], int]:
        page = max(page, 1)
        size = max(size, 1)
        if query or skill or location:
            items = await self._repository.search(query=query, skill=skill, location=location)
            total = len(items)
            return items, total

        items = await self._repository.list(offset=(page - 1) * size, limit=size)
        total = await self._repository.count()
        return items, total

    async def update(self, candidate_id: str, payload: CandidateUpdate) -> Candidate | None:
        candidate = await self._repository.get_by_id(candidate_id)
        if candidate is None:
            return None
        data = payload.model_dump(exclude_unset=True)
        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])
        return await self._repository.update(candidate, **data)

    async def delete(self, candidate_id: str) -> bool:
        candidate = await self._repository.get_by_id(candidate_id)
        if candidate is None:
            return False
        await self._repository.delete(candidate)
        return True
