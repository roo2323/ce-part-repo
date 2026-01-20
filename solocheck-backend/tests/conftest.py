"""
Pytest configuration and fixtures for SoloCheck backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.common.security import create_access_token, get_password_hash
from src.database import Base, get_db
from src.main import app
from src.users.models import User


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
