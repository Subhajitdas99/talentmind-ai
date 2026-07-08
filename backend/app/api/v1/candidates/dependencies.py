from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.service import CandidateService
from app.database.session import get_db_session


async def get_candidate_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> CandidateService:
    """FastAPI dependency for obtaining a request-scoped candidate service."""

    return CandidateService(session)


CandidateServiceDependency = Annotated[CandidateService, Depends(get_candidate_service)]
