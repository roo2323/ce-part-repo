"""
Tests for authentication endpoints.

This module tests user registration, login, token refresh,
and authentication-related functionality.
"""
import pytest
from fastapi.testclient import TestClient

from src.common.security import create_access_token, create_refresh_token


class TestRegister:
    """Tests for user registration endpoint."""

    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securePassword123",
                "nickname": "TestUser",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["nickname"] == "TestUser"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "id" in data

    def test_register_without_nickname(self, client: TestClient):
        """Test registration without nickname."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "nonickname@example.com",
                "password": "securePassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nonickname@example.com"
        assert data["nickname"] is None

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with already existing email."""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "securePassword123",
            },
        )

        # Second registration with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "differentPassword123",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["code"] == "DUPLICATE_EMAIL"

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "securePassword123",
            },
        )

        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test registration with password too short."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "shortpass@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for user login endpoints."""

    @pytest.fixture(autouse=True)
    def setup_user(self, client: TestClient):
        """Create a test user before each test."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "testPassword123",
                "nickname": "LoginUser",
            },
        )

    def test_login_success(self, client: TestClient):
        """Test successful login with form data (OAuth2 compatible)."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "logintest@example.com",
                "password": "testPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_json_success(self, client: TestClient):
        """Test successful login with JSON body."""
        response = client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "logintest@example.com",
                "password": "testPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client: TestClient):
        """Test login with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "logintest@example.com",
                "password": "wrongPassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anyPassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "INVALID_CREDENTIALS"


class TestRefreshToken:
    """Tests for token refresh endpoint."""

    @pytest.fixture
    def tokens(self, client: TestClient):
        """Create a test user and get tokens."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "refreshtest@example.com",
                "password": "testPassword123",
            },
        )
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
        }

    def test_refresh_token_success(self, client: TestClient, tokens: dict):
        """Test successful token refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": tokens["refresh_token"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # New tokens should be different
        assert data["access_token"] != tokens["access_token"]
        assert data["refresh_token"] != tokens["refresh_token"]

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid.token.here",
            },
        )

        assert response.status_code == 401

    def test_refresh_token_with_access_token(self, client: TestClient, tokens: dict):
        """Test that access token cannot be used for refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": tokens["access_token"],
            },
        )

        assert response.status_code == 401


class TestForgotPassword:
    """Tests for forgot password endpoint."""

    def test_forgot_password_existing_email(self, client: TestClient):
        """Test forgot password with existing email."""
        # First create a user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "forgottest@example.com",
                "password": "testPassword123",
            },
        )

        response = client.post(
            "/api/v1/auth/forgot-password",
            json={
                "email": "forgottest@example.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Test forgot password with non-existent email.

        For security, this should return the same response as existing email.
        """
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={
                "email": "nonexistent@example.com",
            },
        )

        # Should return success for security (no email enumeration)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestGetMe:
    """Tests for get current user endpoint."""

    @pytest.fixture
    def auth_headers(self, client: TestClient):
        """Create a test user and get auth headers."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "metest@example.com",
                "password": "testPassword123",
                "nickname": "MeUser",
            },
        )
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}

    def test_get_me_success(self, client: TestClient, auth_headers: dict):
        """Test getting current user info."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "metest@example.com"
        assert data["nickname"] == "MeUser"
        assert data["is_active"] is True
        assert "id" in data

    def test_get_me_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401
