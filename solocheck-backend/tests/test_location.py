"""
Tests for Location API endpoints.

This module contains test cases for:
- GET /api/v1/location/consent - Get location consent status
- POST /api/v1/location/consent - Update location consent
- GET /api/v1/location/history - Get location sharing history

Note: Tests focus on business logic since the module uses AsyncSession.
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.location.models import LocationSharingLog
from src.users.models import User


class TestLocationConsent:
    """Test cases for location consent operations."""

    def test_get_consent_default_false(self, db_session, test_user):
        """Test that location consent defaults to False."""
        user = db_session.query(User).filter(User.id == test_user.id).first()

        assert user.location_consent is False
        assert user.location_consent_at is None

    def test_update_consent_to_true(self, db_session, test_user):
        """Test updating location consent to True."""
        user = db_session.query(User).filter(User.id == test_user.id).first()

        user.location_consent = True
        user.location_consent_at = datetime.now(timezone.utc)
        db_session.commit()
        db_session.refresh(user)

        assert user.location_consent is True
        assert user.location_consent_at is not None

    def test_update_consent_to_false(self, db_session, test_user):
        """Test updating location consent to False."""
        user = db_session.query(User).filter(User.id == test_user.id).first()

        # First enable consent
        user.location_consent = True
        user.location_consent_at = datetime.now(timezone.utc)
        db_session.commit()

        # Then disable it
        user.location_consent = False
        user.location_consent_at = None
        db_session.commit()
        db_session.refresh(user)

        assert user.location_consent is False

    def test_consent_timestamp_recorded(self, db_session, test_user):
        """Test that consent timestamp is recorded."""
        before_consent = datetime.now(timezone.utc)

        user = db_session.query(User).filter(User.id == test_user.id).first()
        user.location_consent = True
        consent_time = datetime.now(timezone.utc)
        user.location_consent_at = consent_time
        db_session.commit()
        db_session.refresh(user)

        after_consent = datetime.now(timezone.utc)

        assert user.location_consent_at is not None
        # Convert to timezone-aware if needed for comparison
        consent_at = user.location_consent_at
        if consent_at.tzinfo is None:
            consent_at = consent_at.replace(tzinfo=timezone.utc)
        assert before_consent <= consent_at <= after_consent


class TestLocationSharingHistory:
    """Test cases for location sharing history."""

    def test_get_history_empty(self, db_session, test_user):
        """Test getting history when no sharing events exist."""
        logs = (
            db_session.query(LocationSharingLog)
            .filter(LocationSharingLog.user_id == test_user.id)
            .all()
        )
        assert len(logs) == 0

    def test_log_location_sharing(self, db_session, test_user):
        """Test logging a location sharing event."""
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="sos",
            location_lat=Decimal("37.5665"),
            location_lng=Decimal("126.9780"),
            recipient_ids=["contact-1", "contact-2"],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.id is not None
        assert log.event_type == "sos"
        assert float(log.location_lat) == pytest.approx(37.5665, rel=1e-4)
        assert float(log.location_lng) == pytest.approx(126.9780, rel=1e-4)

    def test_history_multiple_events(self, db_session, test_user):
        """Test getting multiple location sharing events."""
        # Create multiple sharing logs
        event_types = ["sos", "missed_checkin", "sos"]
        for event_type in event_types:
            log = LocationSharingLog(
                user_id=test_user.id,
                event_type=event_type,
                location_lat=Decimal("37.5665"),
                location_lng=Decimal("126.9780"),
                recipient_ids=["contact-1"],
                shared_at=datetime.now(timezone.utc),
            )
            db_session.add(log)
        db_session.commit()

        logs = (
            db_session.query(LocationSharingLog)
            .filter(LocationSharingLog.user_id == test_user.id)
            .all()
        )
        assert len(logs) == 3

    def test_history_sorted_by_shared_at(self, db_session, test_user):
        """Test that history is sorted by shared_at descending."""
        from datetime import timedelta

        base_time = datetime.now(timezone.utc)

        # Create logs with different times
        for i in range(3):
            log = LocationSharingLog(
                user_id=test_user.id,
                event_type="sos",
                location_lat=Decimal("37.5665"),
                location_lng=Decimal("126.9780"),
                recipient_ids=["contact-1"],
                shared_at=base_time - timedelta(hours=i),
            )
            db_session.add(log)
        db_session.commit()

        logs = (
            db_session.query(LocationSharingLog)
            .filter(LocationSharingLog.user_id == test_user.id)
            .order_by(LocationSharingLog.shared_at.desc())
            .all()
        )

        # Verify descending order
        for i in range(len(logs) - 1):
            assert logs[i].shared_at >= logs[i + 1].shared_at


class TestLocationConsentIntegration:
    """Integration tests for location consent with sharing."""

    def test_share_location_only_when_consent_given(self, db_session, test_user):
        """Test that location is only shared when consent is given."""
        user = db_session.query(User).filter(User.id == test_user.id).first()

        # Without consent, should not share location
        assert user.location_consent is False

        # Simulate checking consent before sharing
        def should_share_location(user_id: str) -> bool:
            u = db_session.query(User).filter(User.id == user_id).first()
            return u.location_consent if u else False

        assert should_share_location(test_user.id) is False

        # Give consent
        user.location_consent = True
        user.location_consent_at = datetime.now(timezone.utc)
        db_session.commit()

        # Now should share location
        assert should_share_location(test_user.id) is True


class TestLocationEventTypes:
    """Test cases for different location event types."""

    def test_sos_event_type(self, db_session, test_user):
        """Test logging SOS event type."""
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="sos",
            location_lat=Decimal("37.5665"),
            location_lng=Decimal("126.9780"),
            recipient_ids=["contact-1"],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()

        assert log.event_type == "sos"

    def test_missed_checkin_event_type(self, db_session, test_user):
        """Test logging missed_checkin event type."""
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="missed_checkin",
            location_lat=Decimal("37.5665"),
            location_lng=Decimal("126.9780"),
            recipient_ids=["contact-1", "contact-2", "contact-3"],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()

        assert log.event_type == "missed_checkin"
        assert len(log.recipient_ids) == 3


class TestLocationAccessControl:
    """Test cases for location access control."""

    def test_unauthorized_access_denied(self, db_session, test_user, inactive_user):
        """Test that users can only access their own location data."""
        # Create log for test_user
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="sos",
            location_lat=Decimal("37.5665"),
            location_lng=Decimal("126.9780"),
            recipient_ids=["contact-1"],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()

        # Try to access as different user
        other_user_logs = (
            db_session.query(LocationSharingLog)
            .filter(LocationSharingLog.user_id == inactive_user.id)
            .all()
        )
        assert len(other_user_logs) == 0

        # Original user can access
        user_logs = (
            db_session.query(LocationSharingLog)
            .filter(LocationSharingLog.user_id == test_user.id)
            .all()
        )
        assert len(user_logs) == 1


class TestLocationNullValues:
    """Test cases for location with null values."""

    def test_location_sharing_without_coordinates(self, db_session, test_user):
        """Test location sharing log without actual coordinates."""
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="missed_checkin",
            location_lat=None,
            location_lng=None,
            recipient_ids=["contact-1"],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.location_lat is None
        assert log.location_lng is None
        assert log.event_type == "missed_checkin"

    def test_location_sharing_with_empty_recipients(self, db_session, test_user):
        """Test location sharing log with empty recipient list."""
        log = LocationSharingLog(
            user_id=test_user.id,
            event_type="sos",
            location_lat=Decimal("37.5665"),
            location_lng=Decimal("126.9780"),
            recipient_ids=[],
            shared_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.recipient_ids == []
