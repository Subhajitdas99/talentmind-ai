from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository, RepositoryError
from app.repositories.factory import RepositoryFactory
from app.repositories.user_repository import UserRepository


def test_repository_factory_builds_typed_repositories() -> None:
    session = object()  # type: ignore[arg-type]
    factory = RepositoryFactory(session)  # type: ignore[arg-type]

    assert isinstance(factory.users(), UserRepository)


def test_repository_error_is_defined() -> None:
    assert RepositoryError.__name__ == "RepositoryError"
