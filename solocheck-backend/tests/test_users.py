"""
Tests for User API endpoints.
"""
import pytest
from fastapi import status


class TestGetMe:
    """Tests for GET /api/v1/users/me endpoint."""

    def test_get_me_success(self, client, auth_headers, test_user):
        """Test successfully retrieving current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == "test@example.com"
        assert data["nickname"] == "TestUser"
        assert data["check_in_cycle"] == 7
        assert data["grace_period"] == 48
        assert data["is_active"] is True

    def test_get_me_unauthorized(self, client):
        """Test accessing profile without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_invalid_token(self, client):
        """Test accessing profile with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_inactive_user(self, client, inactive_auth_headers):
        """Test accessing profile with inactive user account."""
        response = client.get("/api/v1/users/me", headers=inactive_auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateMe:
    """Tests for PUT /api/v1/users/me endpoint."""

    def test_update_me_success(self, client, auth_headers, test_user):
        """Test successfully updating user profile."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"nickname": "UpdatedNickname"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nickname"] == "UpdatedNickname"
        assert data["email"] == test_user.email

    def test_update_me_empty_nickname(self, client, auth_headers):
        """Test updating profile with empty data (no changes)."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_update_me_unauthorized(self, client):
        """Test updating profile without authentication."""
        response = client.put(
            "/api/v1/users/me",
            json={"nickname": "NewNickname"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateFCMToken:
    """Tests for PUT /api/v1/users/me/fcm-token endpoint."""

    def test_update_fcm_token_success(self, client, auth_headers):
        """Test successfully updating FCM token."""
        fcm_token = "test_fcm_token_12345"
        response = client.put(
            "/api/v1/users/me/fcm-token",
            headers=auth_headers,
            json={"fcm_token": fcm_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Note: FCM token is not returned in UserResponse for security
        assert "id" in data

    def test_update_fcm_token_empty(self, client, auth_headers):
        """Test updating FCM token with empty value."""
        response = client.put(
            "/api/v1/users/me/fcm-token",
            headers=auth_headers,
            json={"fcm_token": ""},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_fcm_token_unauthorized(self, client):
        """Test updating FCM token without authentication."""
        response = client.put(
            "/api/v1/users/me/fcm-token",
            json={"fcm_token": "test_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteMe:
    """Tests for DELETE /api/v1/users/me endpoint."""

    def test_delete_me_success(self, client, auth_headers):
        """Test successfully deleting user account."""
        response = client.request(
            "DELETE",
            "/api/v1/users/me",
            headers=auth_headers,
            json={"password": "TestPassword123!"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_me_wrong_password(self, client, auth_headers):
        """Test deleting account with wrong password."""
        response = client.request(
            "DELETE",
            "/api/v1/users/me",
            headers=auth_headers,
            json={"password": "WrongPassword123!"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_me_unauthorized(self, client):
        """Test deleting account without authentication."""
        response = client.request(
            "DELETE",
            "/api/v1/users/me",
            json={"password": "TestPassword123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_me_no_password(self, client, auth_headers):
        """Test deleting account without password."""
        response = client.request(
            "DELETE",
            "/api/v1/users/me",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
