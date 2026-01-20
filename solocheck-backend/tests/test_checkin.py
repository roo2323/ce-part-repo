"""
Tests for check-in API endpoints.

This module contains test cases for:
- POST /api/v1/checkin - Perform check-in
- GET /api/v1/checkin/history - Get check-in history
"""
from datetime import datetime, timedelta, timezone

import pytest

from src.checkin.models import CheckInLog
from src.users.models import User


class TestPerformCheckIn:
    """Test cases for POST /api/v1/checkin endpoint."""

    def test_check_in_success(self, client, auth_headers, test_user):
        """Test successful check-in with default method."""
        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "checked_at" in data
        assert "next_check_in_due" in data
        assert data["message"] == "Check-in successful"

    def test_check_in_with_app_open_method(self, client, auth_headers, test_user):
        """Test check-in with app_open method."""
        response = client.post(
            "/api/v1/checkin",
            json={"method": "app_open"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Check-in successful"

    def test_check_in_with_push_response_method(self, client, auth_headers, test_user):
        """Test check-in with push_response method."""
        response = client.post(
            "/api/v1/checkin",
            json={"method": "push_response"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Check-in successful"

    def test_check_in_updates_last_check_in(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that check-in updates the user's last_check_in timestamp."""
        # Store original last_check_in value
        original_last_check_in = test_user.last_check_in

        # Perform check-in
        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Refresh user from database
        db_session.refresh(test_user)

        # Verify last_check_in was updated
        assert test_user.last_check_in is not None
        if original_last_check_in is not None:
            assert test_user.last_check_in > original_last_check_in

    def test_check_in_creates_log_entry(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that check-in creates a log entry in the database."""
        # Count existing log entries
        initial_count = (
            db_session.query(CheckInLog)
            .filter(CheckInLog.user_id == test_user.id)
            .count()
        )

        # Perform check-in
        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Count log entries after check-in
        final_count = (
            db_session.query(CheckInLog)
            .filter(CheckInLog.user_id == test_user.id)
            .count()
        )

        assert final_count == initial_count + 1

        # Verify the log entry has correct method
        log_entry = (
            db_session.query(CheckInLog)
            .filter(CheckInLog.user_id == test_user.id)
            .order_by(CheckInLog.checked_at.desc())
            .first()
        )
        assert log_entry is not None
        assert log_entry.method == "button_click"

    def test_check_in_returns_correct_next_due(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that check-in returns correct next_check_in_due based on cycle."""
        # Set user's check-in cycle to 7 days
        test_user.check_in_cycle = 7
        db_session.commit()

        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        checked_at = datetime.fromisoformat(data["checked_at"].replace("Z", "+00:00"))
        next_due = datetime.fromisoformat(
            data["next_check_in_due"].replace("Z", "+00:00")
        )

        # next_check_in_due should be approximately 7 days after checked_at
        expected_diff = timedelta(days=7)
        actual_diff = next_due - checked_at

        # Allow some tolerance for processing time
        assert abs((actual_diff - expected_diff).total_seconds()) < 5

    def test_check_in_unauthorized(self, client):
        """Test check-in without authentication."""
        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
        )

        assert response.status_code == 401

    def test_check_in_inactive_user(self, client, inactive_auth_headers):
        """Test check-in with inactive user."""
        response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=inactive_auth_headers,
        )

        # Inactive users should be forbidden
        assert response.status_code == 403


class TestGetCheckInHistory:
    """Test cases for GET /api/v1/checkin/history endpoint."""

    def test_get_history_empty(self, client, auth_headers, test_user):
        """Test getting check-in history when no check-ins exist."""
        response = client.get(
            "/api/v1/checkin/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    def test_get_history_with_check_ins(
        self, client, auth_headers, test_user, db_session
    ):
        """Test getting check-in history with existing check-ins."""
        # Create some check-in logs
        for i in range(3):
            log = CheckInLog(
                user_id=test_user.id,
                checked_at=datetime.now(timezone.utc) - timedelta(days=i),
                method="button_click",
            )
            db_session.add(log)
        db_session.commit()

        response = client.get(
            "/api/v1/checkin/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 3
        assert data["meta"]["total"] == 3

        # Verify each entry has required fields
        for entry in data["data"]:
            assert "id" in entry
            assert "checked_at" in entry
            assert "method" in entry

    def test_get_history_pagination(self, client, auth_headers, test_user, db_session):
        """Test check-in history pagination."""
        # Create 15 check-in logs
        for i in range(15):
            log = CheckInLog(
                user_id=test_user.id,
                checked_at=datetime.now(timezone.utc) - timedelta(hours=i),
                method="button_click",
            )
            db_session.add(log)
        db_session.commit()

        # Get first page with limit 5
        response = client.get(
            "/api/v1/checkin/history",
            params={"page": 1, "limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 5
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 5
        assert data["meta"]["total"] == 15
        assert data["meta"]["total_pages"] == 3

        # Get second page
        response = client.get(
            "/api/v1/checkin/history",
            params={"page": 2, "limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 5
        assert data["meta"]["page"] == 2

    def test_get_history_sorted_by_most_recent(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that history is sorted by most recent first."""
        # Create check-in logs with different timestamps
        times = [
            datetime.now(timezone.utc) - timedelta(days=2),
            datetime.now(timezone.utc) - timedelta(days=1),
            datetime.now(timezone.utc),
        ]

        for t in times:
            log = CheckInLog(
                user_id=test_user.id,
                checked_at=t,
                method="button_click",
            )
            db_session.add(log)
        db_session.commit()

        response = client.get(
            "/api/v1/checkin/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify order is descending (most recent first)
        timestamps = [
            datetime.fromisoformat(entry["checked_at"].replace("Z", "+00:00"))
            for entry in data["data"]
        ]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_get_history_unauthorized(self, client):
        """Test getting history without authentication."""
        response = client.get("/api/v1/checkin/history")

        assert response.status_code == 401

    def test_get_history_limit_max_100(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that limit is capped at 100."""
        # Create 5 check-in logs
        for i in range(5):
            log = CheckInLog(
                user_id=test_user.id,
                checked_at=datetime.now(timezone.utc) - timedelta(hours=i),
                method="button_click",
            )
            db_session.add(log)
        db_session.commit()

        # Request with limit > 100
        response = client.get(
            "/api/v1/checkin/history",
            params={"page": 1, "limit": 200},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Limit should be capped at 100
        assert data["meta"]["limit"] == 100
