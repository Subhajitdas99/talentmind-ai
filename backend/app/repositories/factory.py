from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.models import User
from app.api.v1.candidates.models import Candidate
from app.models.domain import Job, Recruiter, Resume
from app.repositories.base import BaseRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository


class RepositoryFactory:
    """Factory for retrieving typed repositories from a shared async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def users(self) -> UserRepository:
        return UserRepository(self._session)

    def candidates(self) -> CandidateRepository:
        return CandidateRepository(self._session)

    def jobs(self) -> JobRepository:
        return JobRepository(self._session)

    def recruiters(self) -> BaseRepository[Recruiter]:
        return BaseRepository(self._session, Recruiter)

    def resumes(self) -> BaseRepository[Resume]:
        return BaseRepository(self._session, Resume)

    def generic(self, model: type[object]) -> BaseRepository[object]:
        return BaseRepository(self._session, model)
