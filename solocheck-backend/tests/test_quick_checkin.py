"""
Tests for Quick Check-in API endpoints.

This module contains test cases for:
- POST /api/v1/checkin/quick - Quick check-in via session token
- Session token generation and verification
"""
from datetime import datetime, timedelta, timezone

import pytest

from src.checkin.models import CheckInLog, CheckInSessionToken
from src.checkin.service import (
    generate_session_token,
    verify_and_consume_session_token,
    create_quick_check_in_with_token,
    cleanup_expired_tokens,
)


class TestGenerateSessionToken:
    """Test cases for session token generation."""

    def test_generate_session_token(self, db_session, test_user):
        """Test generating a session token."""
        session_token = generate_session_token(db_session, test_user.id)

        assert session_token is not None
        assert session_token.token is not None
        assert len(session_token.token) > 0
        assert session_token.user_id == test_user.id
        assert session_token.expires_at is not None
        assert session_token.used_at is None

    def test_token_expires_after_1_hour(self, db_session, test_user):
        """Test that token expires after 1 hour by default."""
        before = datetime.now(timezone.utc)
        session_token = generate_session_token(db_session, test_user.id)
        after = datetime.now(timezone.utc)

        expected_min = before + timedelta(hours=1)
        expected_max = after + timedelta(hours=1)

        # Handle timezone-naive comparison
        expires_at = session_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        assert expected_min <= expires_at <= expected_max

    def test_generate_token_custom_expiry(self, db_session, test_user):
        """Test generating token with custom expiry time."""
        session_token = generate_session_token(
            db_session, test_user.id, expires_hours=2
        )

        now = datetime.now(timezone.utc)
        expected = now + timedelta(hours=2)

        # Handle timezone-naive comparison
        expires_at = session_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Allow 5 seconds tolerance
        diff = abs((expires_at - expected).total_seconds())
        assert diff < 5

    def test_generate_token_for_nonexistent_user(self, db_session):
        """Test generating token for non-existent user returns None."""
        session_token = generate_session_token(db_session, "nonexistent-user-id")
        assert session_token is None


class TestVerifySessionToken:
    """Test cases for session token verification."""

    def test_verify_valid_token(self, db_session, test_user):
        """Test verifying a valid token returns the user."""
        session_token = generate_session_token(db_session, test_user.id)

        user = verify_and_consume_session_token(db_session, session_token.token)

        assert user is not None
        assert user.id == test_user.id

        # Token should be marked as used
        db_session.refresh(session_token)
        assert session_token.used_at is not None

    def test_verify_expired_token_fails(self, db_session, test_user):
        """Test that expired token verification fails."""
        # Create a token that's already expired
        session_token = CheckInSessionToken(
            user_id=test_user.id,
            token="test-expired-token-12345",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(session_token)
        db_session.commit()

        user = verify_and_consume_session_token(db_session, session_token.token)
        assert user is None

    def test_verify_used_token_fails(self, db_session, test_user):
        """Test that already-used token verification fails."""
        session_token = generate_session_token(db_session, test_user.id)

        # First use
        user1 = verify_and_consume_session_token(db_session, session_token.token)
        assert user1 is not None

        # Second use should fail
        user2 = verify_and_consume_session_token(db_session, session_token.token)
        assert user2 is None

    def test_verify_nonexistent_token_fails(self, db_session):
        """Test that non-existent token verification fails."""
        user = verify_and_consume_session_token(db_session, "nonexistent-token")
        assert user is None


class TestQuickCheckIn:
    """Test cases for quick check-in functionality."""

    def test_quick_checkin_with_valid_token(self, db_session, test_user):
        """Test quick check-in with valid token."""
        session_token = generate_session_token(db_session, test_user.id)

        result = create_quick_check_in_with_token(db_session, session_token.token)

        assert result is not None
        check_in_log, next_due, user = result

        assert check_in_log is not None
        assert check_in_log.method == "push_response"
        assert check_in_log.user_id == test_user.id
        assert next_due is not None
        assert user.id == test_user.id

    def test_quick_checkin_invalid_token(self, db_session):
        """Test quick check-in with invalid token returns None."""
        result = create_quick_check_in_with_token(db_session, "invalid-token")
        assert result is None

    def test_quick_checkin_updates_last_checkin(self, db_session, test_user):
        """Test that quick check-in updates user's last_check_in."""
        original_last_checkin = test_user.last_check_in
        session_token = generate_session_token(db_session, test_user.id)

        create_quick_check_in_with_token(db_session, session_token.token)

        db_session.refresh(test_user)
        assert test_user.last_check_in is not None
        if original_last_checkin is not None:
            assert test_user.last_check_in > original_last_checkin

    def test_quick_checkin_creates_log_entry(self, db_session, test_user):
        """Test that quick check-in creates a log entry."""
        initial_count = (
            db_session.query(CheckInLog)
            .filter(CheckInLog.user_id == test_user.id)
            .count()
        )

        session_token = generate_session_token(db_session, test_user.id)
        create_quick_check_in_with_token(db_session, session_token.token)

        final_count = (
            db_session.query(CheckInLog)
            .filter(CheckInLog.user_id == test_user.id)
            .count()
        )

        assert final_count == initial_count + 1


class TestQuickCheckInAPI:
    """Test cases for POST /api/v1/checkin/quick endpoint."""

    def test_quick_checkin_api_success(self, client, db_session, test_user):
        """Test quick check-in API with valid token."""
        session_token = generate_session_token(db_session, test_user.id)

        response = client.post(
            "/api/v1/checkin/quick",
            json={
                "token": session_token.token,
                "device_type": "push",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["id"] is not None
        assert data["checked_at"] is not None
        assert data["next_check_in_due"] is not None

    def test_quick_checkin_api_invalid_token(self, client):
        """Test quick check-in API with invalid token."""
        response = client.post(
            "/api/v1/checkin/quick",
            json={
                "token": "invalid-token-123",
                "device_type": "push",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is False
        assert "유효하지 않거나 만료된 토큰" in data["message"]

    def test_quick_checkin_no_auth_required(self, client, db_session, test_user):
        """Test that quick check-in doesn't require auth header."""
        session_token = generate_session_token(db_session, test_user.id)

        # No auth header provided
        response = client.post(
            "/api/v1/checkin/quick",
            json={
                "token": session_token.token,
                "device_type": "push",
            },
        )

        # Should succeed without auth
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTokenCleanup:
    """Test cases for token cleanup functionality."""

    def test_cleanup_expired_tokens(self, db_session, test_user):
        """Test cleaning up expired tokens."""
        # Create expired token
        expired_token = CheckInSessionToken(
            user_id=test_user.id,
            token="expired-token-1",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db_session.add(expired_token)

        # Create valid token
        valid_token = CheckInSessionToken(
            user_id=test_user.id,
            token="valid-token-1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(valid_token)
        db_session.commit()

        deleted_count = cleanup_expired_tokens(db_session)

        assert deleted_count >= 1

        # Valid token should still exist
        remaining = (
            db_session.query(CheckInSessionToken)
            .filter(CheckInSessionToken.token == "valid-token-1")
            .first()
        )
        assert remaining is not None

    def test_cleanup_old_used_tokens(self, db_session, test_user):
        """Test cleaning up old used tokens."""
        # Create used token from yesterday
        old_used_token = CheckInSessionToken(
            user_id=test_user.id,
            token="old-used-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            used_at=datetime.now(timezone.utc) - timedelta(hours=25),
        )
        db_session.add(old_used_token)
        db_session.commit()

        deleted_count = cleanup_expired_tokens(db_session)

        assert deleted_count >= 1

        # Old used token should be deleted
        remaining = (
            db_session.query(CheckInSessionToken)
            .filter(CheckInSessionToken.token == "old-used-token")
            .first()
        )
        assert remaining is None
