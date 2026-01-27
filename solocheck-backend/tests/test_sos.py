"""
Tests for SOS API endpoints.

This module contains test cases for:
- POST /api/v1/sos/trigger - Trigger SOS
- POST /api/v1/sos/{sos_id}/cancel - Cancel SOS
- GET /api/v1/sos/status - Get SOS status
"""
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from src.sos.models import SOSEvent, SOS_STATUS_TRIGGERED, SOS_STATUS_CANCELLED, SOS_STATUS_SENT
from src.sos.service import (
    trigger_sos,
    cancel_sos,
    get_active_sos,
    get_user_sos_history,
    is_sos_still_active,
    mark_sos_sent,
)


class TestTriggerSOS:
    """Test cases for POST /api/v1/sos/trigger endpoint."""

    @patch("src.scheduler.tasks.send_sos_alerts_delayed")
    def test_trigger_sos_creates_event(
        self, mock_task, client, auth_headers, test_user, db_session
    ):
        """Test that triggering SOS creates an event."""
        mock_task.apply_async = MagicMock()

        response = client.post(
            "/api/v1/sos/trigger",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert "event" in data
        assert data["event"]["status"] == SOS_STATUS_TRIGGERED
        assert data["event"]["user_id"] == test_user.id
        assert data["countdown_seconds"] == 5

        # Verify task was scheduled
        mock_task.apply_async.assert_called_once()

    @patch("src.scheduler.tasks.send_sos_alerts_delayed")
    def test_trigger_sos_with_location(
        self, mock_task, client, auth_headers, test_user, db_session
    ):
        """Test triggering SOS with location data."""
        mock_task.apply_async = MagicMock()

        response = client.post(
            "/api/v1/sos/trigger",
            json={
                "location_lat": 37.5665,
                "location_lng": 126.9780,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["event"]["location_lat"] == pytest.approx(37.5665, rel=1e-4)
        assert data["event"]["location_lng"] == pytest.approx(126.9780, rel=1e-4)

    @patch("src.scheduler.tasks.send_sos_alerts_delayed")
    def test_trigger_sos_without_location(
        self, mock_task, client, auth_headers, test_user
    ):
        """Test triggering SOS without location data."""
        mock_task.apply_async = MagicMock()

        response = client.post(
            "/api/v1/sos/trigger",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["event"]["location_lat"] is None
        assert data["event"]["location_lng"] is None

    @patch("src.scheduler.tasks.send_sos_alerts_delayed")
    def test_trigger_sos_returns_countdown(
        self, mock_task, client, auth_headers, test_user
    ):
        """Test that trigger response includes countdown."""
        mock_task.apply_async = MagicMock()

        response = client.post(
            "/api/v1/sos/trigger",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert "countdown_seconds" in data
        assert data["countdown_seconds"] == 5

    def test_trigger_sos_unauthorized(self, client):
        """Test triggering SOS without authentication."""
        response = client.post(
            "/api/v1/sos/trigger",
            json={},
        )

        assert response.status_code == 401


class TestCancelSOS:
    """Test cases for POST /api/v1/sos/{sos_id}/cancel endpoint."""

    def test_cancel_sos_within_countdown(
        self, client, auth_headers, test_user, db_session
    ):
        """Test cancelling SOS within countdown period."""
        # Create an active SOS event
        sos_event = SOSEvent(
            user_id=test_user.id,
            triggered_at=datetime.now(timezone.utc),
            status=SOS_STATUS_TRIGGERED,
        )
        db_session.add(sos_event)
        db_session.commit()
        db_session.refresh(sos_event)

        response = client.post(
            f"/api/v1/sos/{sos_event.id}/cancel",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["event"]["status"] == SOS_STATUS_CANCELLED
        assert data["event"]["cancelled_at"] is not None

    def test_cancel_sos_already_sent_fails(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that cancelling already-sent SOS fails."""
        # Create an already-sent SOS event
        sos_event = SOSEvent(
            user_id=test_user.id,
            triggered_at=datetime.now(timezone.utc),
            status=SOS_STATUS_SENT,
            sent_at=datetime.now(timezone.utc),
        )
        db_session.add(sos_event)
        db_session.commit()
        db_session.refresh(sos_event)

        response = client.post(
            f"/api/v1/sos/{sos_event.id}/cancel",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_cancel_nonexistent_sos_fails(self, client, auth_headers, test_user):
        """Test cancelling non-existent SOS returns 404."""
        response = client.post(
            "/api/v1/sos/nonexistent-id/cancel",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_cancel_other_user_sos_fails(
        self, client, auth_headers, test_user, db_session, inactive_user
    ):
        """Test that user cannot cancel another user's SOS."""
        # Create SOS for different user
        sos_event = SOSEvent(
            user_id=inactive_user.id,
            triggered_at=datetime.now(timezone.utc),
            status=SOS_STATUS_TRIGGERED,
        )
        db_session.add(sos_event)
        db_session.commit()
        db_session.refresh(sos_event)

        response = client.post(
            f"/api/v1/sos/{sos_event.id}/cancel",
            headers=auth_headers,
        )

        # Should fail because it belongs to different user
        assert response.status_code == 404


class TestSOSStatus:
    """Test cases for GET /api/v1/sos/status endpoint."""

    def test_get_active_sos_event(
        self, client, auth_headers, test_user, db_session
    ):
        """Test getting status when active SOS exists."""
        # Create an active SOS event
        sos_event = SOSEvent(
            user_id=test_user.id,
            triggered_at=datetime.now(timezone.utc),
            status=SOS_STATUS_TRIGGERED,
        )
        db_session.add(sos_event)
        db_session.commit()

        response = client.get(
            "/api/v1/sos/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["has_active_sos"] is True
        assert data["active_event"] is not None
        assert data["active_event"]["status"] == SOS_STATUS_TRIGGERED

    def test_get_status_no_active_sos(self, client, auth_headers, test_user):
        """Test getting status when no active SOS."""
        response = client.get(
            "/api/v1/sos/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["has_active_sos"] is False
        assert data["active_event"] is None

    def test_get_status_unauthorized(self, client):
        """Test getting status without authentication."""
        response = client.get("/api/v1/sos/status")

        assert response.status_code == 401


class TestSOSServiceFunctions:
    """Test cases for SOS service layer functions."""

    def test_sos_status_triggered_to_cancelled(self, db_session, test_user):
        """Test SOS status transition from triggered to cancelled."""
        sos_event = trigger_sos(db_session, test_user.id)
        assert sos_event.status == SOS_STATUS_TRIGGERED

        cancelled_event = cancel_sos(db_session, test_user.id, sos_event.id)
        assert cancelled_event.status == SOS_STATUS_CANCELLED
        assert cancelled_event.cancelled_at is not None

    def test_sos_status_triggered_to_sent(self, db_session, test_user):
        """Test SOS status transition from triggered to sent."""
        sos_event = trigger_sos(db_session, test_user.id)
        assert sos_event.status == SOS_STATUS_TRIGGERED

        sent_event = mark_sos_sent(db_session, sos_event.id)
        assert sent_event.status == SOS_STATUS_SENT
        assert sent_event.sent_at is not None

    def test_get_sos_history(self, db_session, test_user):
        """Test getting SOS history for user."""
        # Create multiple SOS events
        for _ in range(3):
            sos = trigger_sos(db_session, test_user.id)
            cancel_sos(db_session, test_user.id, sos.id)

        history = get_user_sos_history(db_session, test_user.id)
        assert len(history) == 3

    def test_is_sos_still_active(self, db_session, test_user):
        """Test checking if SOS is still active."""
        sos_event = trigger_sos(db_session, test_user.id)

        assert is_sos_still_active(db_session, sos_event.id) is True

        cancel_sos(db_session, test_user.id, sos_event.id)
        assert is_sos_still_active(db_session, sos_event.id) is False

    def test_get_active_sos_returns_most_recent(self, db_session, test_user):
        """Test that get_active_sos returns the most recent triggered event."""
        # Create and cancel first SOS
        sos1 = trigger_sos(db_session, test_user.id)
        cancel_sos(db_session, test_user.id, sos1.id)

        # Create second active SOS
        sos2 = trigger_sos(db_session, test_user.id)

        active = get_active_sos(db_session, test_user.id)
        assert active is not None
        assert active.id == sos2.id
