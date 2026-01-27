"""
Tests for Settings API endpoints (Reminder Settings).

This module contains test cases for:
- GET /api/v1/settings/reminder - Get reminder settings
- PUT /api/v1/settings/reminder - Update reminder settings
- DELETE /api/v1/settings/reminder/quiet-hours - Clear quiet hours
"""
from datetime import time

import pytest

from src.settings.models import ReminderSettings
from src.settings.service import is_in_quiet_hours, should_send_reminder


class TestGetReminderSettings:
    """Test cases for GET /api/v1/settings/reminder endpoint."""

    def test_get_reminder_settings_default(self, client, auth_headers, test_user):
        """Test getting default reminder settings when none exist."""
        response = client.get(
            "/api/v1/settings/reminder",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Default values
        assert data["reminder_hours_before"] == [48, 24, 12]
        assert data["push_enabled"] is True
        assert data["email_enabled"] is False
        assert data["quiet_hours_start"] is None
        assert data["quiet_hours_end"] is None
        assert data["preferred_time"] is None
        assert data["custom_message"] is None

    def test_get_reminder_settings_unauthorized(self, client):
        """Test getting reminder settings without authentication."""
        response = client.get("/api/v1/settings/reminder")

        assert response.status_code == 401


class TestUpdateReminderSettings:
    """Test cases for PUT /api/v1/settings/reminder endpoint."""

    def test_update_reminder_hours_before(self, client, auth_headers, test_user):
        """Test updating reminder_hours_before."""
        response = client.put(
            "/api/v1/settings/reminder",
            json={"reminder_hours_before": [72, 48, 24]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "settings" in data
        # Hours should be sorted in descending order
        assert data["settings"]["reminder_hours_before"] == [72, 48, 24]

    def test_update_quiet_hours(self, client, auth_headers, test_user):
        """Test updating quiet hours."""
        response = client.put(
            "/api/v1/settings/reminder",
            json={
                "quiet_hours_start": "22:00:00",
                "quiet_hours_end": "08:00:00",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["settings"]["quiet_hours_start"] == "22:00:00"
        assert data["settings"]["quiet_hours_end"] == "08:00:00"

    def test_update_preferred_time(self, client, auth_headers, test_user):
        """Test updating preferred time for reminders."""
        response = client.put(
            "/api/v1/settings/reminder",
            json={"preferred_time": "09:00:00"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["settings"]["preferred_time"] == "09:00:00"

    def test_toggle_push_enabled(self, client, auth_headers, test_user):
        """Test toggling push notifications."""
        # Disable push
        response = client.put(
            "/api/v1/settings/reminder",
            json={"push_enabled": False},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["push_enabled"] is False

        # Enable push
        response = client.put(
            "/api/v1/settings/reminder",
            json={"push_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["push_enabled"] is True

    def test_toggle_email_enabled(self, client, auth_headers, test_user):
        """Test toggling email notifications."""
        response = client.put(
            "/api/v1/settings/reminder",
            json={"email_enabled": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["email_enabled"] is True

    def test_set_custom_message(self, client, auth_headers, test_user):
        """Test setting custom reminder message."""
        custom_msg = "Please check in soon!"
        response = client.put(
            "/api/v1/settings/reminder",
            json={"custom_message": custom_msg},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["custom_message"] == custom_msg

    def test_update_multiple_settings(self, client, auth_headers, test_user):
        """Test updating multiple settings at once."""
        response = client.put(
            "/api/v1/settings/reminder",
            json={
                "reminder_hours_before": [48, 24],
                "push_enabled": True,
                "email_enabled": True,
                "custom_message": "Stay safe!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["settings"]["reminder_hours_before"] == [48, 24]
        assert data["settings"]["push_enabled"] is True
        assert data["settings"]["email_enabled"] is True
        assert data["settings"]["custom_message"] == "Stay safe!"


class TestClearQuietHours:
    """Test cases for DELETE /api/v1/settings/reminder/quiet-hours endpoint."""

    def test_clear_quiet_hours(self, client, auth_headers, test_user, db_session):
        """Test clearing quiet hours settings."""
        # First set quiet hours
        client.put(
            "/api/v1/settings/reminder",
            json={
                "quiet_hours_start": "22:00:00",
                "quiet_hours_end": "08:00:00",
            },
            headers=auth_headers,
        )

        # Then clear them
        response = client.delete(
            "/api/v1/settings/reminder/quiet-hours",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["settings"]["quiet_hours_start"] is None
        assert data["settings"]["quiet_hours_end"] is None


class TestQuietHoursLogic:
    """Test cases for quiet hours business logic."""

    def test_is_in_quiet_hours_same_day_range(self, db_session, test_user):
        """Test quiet hours check for same-day range (e.g., 09:00 to 17:00)."""
        settings = ReminderSettings(
            user_id=test_user.id,
            quiet_hours_start=time(9, 0),
            quiet_hours_end=time(17, 0),
        )
        db_session.add(settings)
        db_session.commit()

        # Within quiet hours
        assert is_in_quiet_hours(settings, time(12, 0)) is True
        assert is_in_quiet_hours(settings, time(9, 0)) is True
        assert is_in_quiet_hours(settings, time(17, 0)) is True

        # Outside quiet hours
        assert is_in_quiet_hours(settings, time(8, 0)) is False
        assert is_in_quiet_hours(settings, time(18, 0)) is False

    def test_is_in_quiet_hours_overnight_range(self, db_session, test_user):
        """Test quiet hours check for overnight range (e.g., 22:00 to 08:00)."""
        settings = ReminderSettings(
            user_id=test_user.id,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(8, 0),
        )
        db_session.add(settings)
        db_session.commit()

        # Within quiet hours (evening)
        assert is_in_quiet_hours(settings, time(23, 0)) is True
        # Within quiet hours (morning)
        assert is_in_quiet_hours(settings, time(7, 0)) is True

        # Outside quiet hours
        assert is_in_quiet_hours(settings, time(12, 0)) is False
        assert is_in_quiet_hours(settings, time(21, 0)) is False

    def test_is_in_quiet_hours_no_settings(self, db_session, test_user):
        """Test quiet hours check when not configured."""
        settings = ReminderSettings(
            user_id=test_user.id,
            quiet_hours_start=None,
            quiet_hours_end=None,
        )
        db_session.add(settings)
        db_session.commit()

        # Should always return False when quiet hours not set
        assert is_in_quiet_hours(settings, time(12, 0)) is False


class TestShouldSendReminder:
    """Test cases for should_send_reminder logic."""

    def test_should_send_reminder_within_threshold(
        self, db_session, test_user
    ):
        """Test reminder should be sent when within threshold."""
        # Create settings
        settings = ReminderSettings(
            user_id=test_user.id,
            reminder_hours_before=[48, 24, 12],
            push_enabled=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Test with 24 hours remaining (matches threshold)
        should_send, message = should_send_reminder(db_session, test_user, 24)
        assert should_send is True

    def test_should_send_reminder_push_disabled(
        self, db_session, test_user
    ):
        """Test reminder should not be sent when push is disabled."""
        settings = ReminderSettings(
            user_id=test_user.id,
            reminder_hours_before=[48, 24, 12],
            push_enabled=False,
        )
        db_session.add(settings)
        db_session.commit()

        should_send, _ = should_send_reminder(db_session, test_user, 24)
        assert should_send is False
