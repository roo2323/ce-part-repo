"""
Pytest configuration and fixtures for SoloCheck backend tests.
"""
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import JSON, Text, TypeDecorator

from src.common.security import create_access_token, get_password_hash
from src.database import Base, get_db
from src.main import app
from src.users.models import User


# Monkey-patch ARRAY type for SQLite compatibility
# This allows the models to use ARRAY while testing with SQLite
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY


class SQLiteCompatibleArray(TypeDecorator):
    """A TypeDecorator that stores PostgreSQL ARRAY as JSON in SQLite."""

    impl = Text
    cache_ok = True

    def __init__(self, item_type=None):
        super().__init__()
        self.item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(self.item_type))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            if isinstance(value, str):
                return json.loads(value)
        return value


# Patch the ARRAY class methods for SQLite
original_array_bind_processor = PG_ARRAY.bind_processor.__get__(PG_ARRAY, type)


def patched_bind_processor(self, dialect):
    """Override bind_processor to handle SQLite."""
    if dialect.name != "postgresql":
        def process(value):
            if value is not None:
                return json.dumps(value)
            return value
        return process
    return original_array_bind_processor(self, dialect)


def patched_result_processor(self, dialect, coltype):
    """Override result_processor to handle SQLite."""
    if dialect.name != "postgresql":
        def process(value):
            if value is not None and isinstance(value, str):
                return json.loads(value)
            return value
        return process
    # For PostgreSQL, use default behavior
    return None


# Apply patches
PG_ARRAY.bind_processor = patched_bind_processor
PG_ARRAY.result_processor = patched_result_processor


def visit_ARRAY_as_TEXT(self, type_, **kw):
    """Render ARRAY as TEXT for SQLite."""
    return "TEXT"


sqlite.base.SQLiteTypeCompiler.visit_ARRAY = visit_ARRAY_as_TEXT

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    """Create a test user for authenticated tests."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        nickname="TestUser",
        check_in_cycle=7,
        grace_period=48,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_token(test_user) -> str:
    """Create a valid access token for the test user."""
    token_data = {"sub": test_user.id, "email": test_user.email}
    return create_access_token(token_data)


@pytest.fixture(scope="function")
def auth_headers(test_user_token) -> dict:
    """Create authorization headers with the test user's token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture(scope="function")
def inactive_user(db_session) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        nickname="InactiveUser",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def inactive_user_token(inactive_user) -> str:
    """Create a valid access token for the inactive user."""
    token_data = {"sub": inactive_user.id, "email": inactive_user.email}
    return create_access_token(token_data)


@pytest.fixture(scope="function")
def inactive_auth_headers(inactive_user_token) -> dict:
    """Create authorization headers with the inactive user's token."""
    return {"Authorization": f"Bearer {inactive_user_token}"}
