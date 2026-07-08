from app.database.base import DatabaseFactory
from app.database.dependencies import get_database_factory, get_session_manager
from app.database.session import SessionManager


def test_database_factory_is_cached_per_process() -> None:
    factory_one = get_database_factory()
    factory_two = get_database_factory()

    assert isinstance(factory_one, DatabaseFactory)
    assert factory_one is factory_two


def test_session_manager_is_cached_per_process() -> None:
    manager_one = get_session_manager()
    manager_two = get_session_manager()

    assert isinstance(manager_one, SessionManager)
    assert manager_one is manager_two
