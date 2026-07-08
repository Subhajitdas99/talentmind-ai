from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.models import Candidate
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Repository with candidate-specific query helpers."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Candidate)

    async def search(self, *, query: str | None = None, skill: str | None = None, location: str | None = None) -> list[Candidate]:
        statement = select(Candidate)
        filters = []
        if query:
            filters.append(or_(Candidate.full_name.ilike(f"%{query}%"), Candidate.summary.ilike(f"%{query}%")))
        if skill:
            filters.append(Candidate.skills.ilike(f"%{skill}%"))
        if location:
            filters.append(Candidate.location.ilike(f"%{location}%"))
        if filters:
            statement = statement.where(*filters)
        result = await self._session.execute(statement)
        return list(result.scalars().all())
