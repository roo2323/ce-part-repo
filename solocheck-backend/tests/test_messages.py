"""
Tests for Personal Message API endpoints.

This module contains tests for message CRUD operations including
encryption, validation, and authentication.
"""
import pytest


class TestSaveMessage:
    """Test cases for saving personal messages."""

    def test_save_message_success(self, client, auth_headers):
        """Test successful message creation."""
        response = client.put(
            "/api/v1/message",
            json={
                "content": "This is my personal message to my emergency contacts.",
                "is_enabled": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "This is my personal message to my emergency contacts."
        assert data["is_enabled"] is True
        assert data["character_count"] == len("This is my personal message to my emergency contacts.")
        assert data["max_characters"] == 2000
        assert data["id"] is not None
        assert data["updated_at"] is not None

    def test_save_message_update_existing(self, client, auth_headers):
        """Test updating an existing message."""
        # First, create a message
        client.put(
            "/api/v1/message",
            json={"content": "Original message", "is_enabled": True},
            headers=auth_headers,
        )

        # Update the message
        response = client.put(
            "/api/v1/message",
            json={"content": "Updated message", "is_enabled": False},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated message"
        assert data["is_enabled"] is False

    def test_save_message_too_long(self, client, auth_headers):
        """Test saving a message that exceeds 2000 characters."""
        long_content = "a" * 2001

        response = client.put(
            "/api/v1/message",
            json={"content": long_content, "is_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_save_message_max_length(self, client, auth_headers):
        """Test saving a message at exactly 2000 characters."""
        max_content = "a" * 2000

        response = client.put(
            "/api/v1/message",
            json={"content": max_content, "is_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["character_count"] == 2000

    def test_save_message_empty_content(self, client, auth_headers):
        """Test saving an empty message (should fail)."""
        response = client.put(
            "/api/v1/message",
            json={"content": "", "is_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_save_message_unauthorized(self, client):
        """Test saving a message without authentication."""
        response = client.put(
            "/api/v1/message",
            json={"content": "Test message", "is_enabled": True},
        )

        assert response.status_code == 401


class TestGetMessage:
    """Test cases for retrieving personal messages."""

    def test_get_message_success(self, client, auth_headers):
        """Test getting an existing message."""
        # First, create a message
        client.put(
            "/api/v1/message",
            json={"content": "Test message content", "is_enabled": True},
            headers=auth_headers,
        )

        # Get the message
        response = client.get("/api/v1/message", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Test message content"
        assert data["is_enabled"] is True
        assert data["character_count"] == len("Test message content")
        assert data["max_characters"] == 2000

    def test_get_message_not_found(self, client, auth_headers):
        """Test getting a message when none exists."""
        response = client.get("/api/v1/message", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] is None
        assert data["content"] is None
        assert data["is_enabled"] is False
        assert data["character_count"] == 0
        assert data["max_characters"] == 2000

    def test_get_message_unauthorized(self, client):
        """Test getting a message without authentication."""
        response = client.get("/api/v1/message")

        assert response.status_code == 401

    def test_get_message_inactive_user(self, client, inactive_auth_headers):
        """Test getting a message with an inactive user account."""
        response = client.get("/api/v1/message", headers=inactive_auth_headers)

        assert response.status_code == 403


class TestDeleteMessage:
    """Test cases for deleting personal messages."""

    def test_delete_message_success(self, client, auth_headers):
        """Test successful message deletion."""
        # First, create a message
        client.put(
            "/api/v1/message",
            json={"content": "Message to delete", "is_enabled": True},
            headers=auth_headers,
        )

        # Delete the message
        response = client.delete("/api/v1/message", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        assert data["message"] == "Message deleted successfully"

        # Verify it's deleted
        get_response = client.get("/api/v1/message", headers=auth_headers)
        assert get_response.json()["content"] is None

    def test_delete_message_not_found(self, client, auth_headers):
        """Test deleting a message when none exists."""
        response = client.delete("/api/v1/message", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is False
        assert data["message"] == "No message to delete"

    def test_delete_message_unauthorized(self, client):
        """Test deleting a message without authentication."""
        response = client.delete("/api/v1/message")

        assert response.status_code == 401


class TestMessageEncryption:
    """Test cases verifying encryption functionality."""

    def test_message_encryption_roundtrip(self, client, auth_headers, db_session):
        """Test that messages are encrypted in storage and decrypted on retrieval."""
        from src.messages.models import PersonalMessage

        original_content = "Secret message content"

        # Save the message
        client.put(
            "/api/v1/message",
            json={"content": original_content, "is_enabled": True},
            headers=auth_headers,
        )

        # Check that stored content is encrypted (different from original)
        stored_message = db_session.query(PersonalMessage).first()
        assert stored_message is not None
        assert stored_message.content != original_content

        # Verify that retrieval decrypts correctly
        response = client.get("/api/v1/message", headers=auth_headers)
        assert response.json()["content"] == original_content

    def test_message_special_characters(self, client, auth_headers):
        """Test that special characters are handled correctly."""
        special_content = "Hello! 안녕하세요! 🙂 Special chars: <>&'\""

        response = client.put(
            "/api/v1/message",
            json={"content": special_content, "is_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Retrieve and verify
        get_response = client.get("/api/v1/message", headers=auth_headers)
        assert get_response.json()["content"] == special_content
