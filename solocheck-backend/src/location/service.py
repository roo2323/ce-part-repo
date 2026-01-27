"""
Location service for SoloCheck.

Business logic for location consent and sharing operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.location.models import LocationSharingLog
from src.location.schemas import LocationData
from src.users.models import User


class LocationService:
    """Service for location operations."""

    @staticmethod
    def update_location_consent(
        db: Session, user_id: str, consent: bool
    ) -> tuple[bool, Optional[datetime]]:
        """Update user's location consent."""
        consent_at = datetime.utcnow() if consent else None

        db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                location_consent=consent,
                location_consent_at=consent_at,
            )
        )
        db.commit()

        return consent, consent_at

    @staticmethod
    def get_location_consent(
        db: Session, user_id: str
    ) -> tuple[bool, Optional[datetime]]:
        """Get user's location consent status."""
        result = db.execute(
            select(User.location_consent, User.location_consent_at).where(
                User.id == user_id
            )
        )
        row = result.one_or_none()
        if row:
            return row.location_consent, row.location_consent_at
        return False, None

    @staticmethod
    def has_location_consent(db: Session, user_id: str) -> bool:
        """Check if user has given location consent."""
        consent, _ = LocationService.get_location_consent(db, user_id)
        return consent

    @staticmethod
    def log_location_sharing(
        db: Session,
        user_id: str,
        event_type: str,
        location: Optional[LocationData],
        recipient_ids: list[str],
    ) -> LocationSharingLog:
        """Log a location sharing event (legal requirement)."""
        log = LocationSharingLog(
            user_id=user_id,
            event_type=event_type,
            location_lat=Decimal(str(location.lat)) if location else None,
            location_lng=Decimal(str(location.lng)) if location else None,
            recipient_ids=recipient_ids,
            shared_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_location_sharing_history(
        db: Session, user_id: str, limit: int = 50
    ) -> list[LocationSharingLog]:
        """Get user's location sharing history."""
        result = db.execute(
            select(LocationSharingLog)
            .where(LocationSharingLog.user_id == user_id)
            .order_by(LocationSharingLog.shared_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    def share_location_with_contacts(
        db: Session,
        user_id: str,
        location: Optional[LocationData],
        event_type: str,
        contact_ids: list[str],
    ) -> Optional[LocationSharingLog]:
        """
        Share location with contacts and log the sharing event.

        Returns the log entry if location was shared, None if user hasn't consented.
        """
        # Check consent
        has_consent = LocationService.has_location_consent(db, user_id)
        if not has_consent or not location:
            return None

        # Log the sharing event
        log = LocationService.log_location_sharing(
            db=db,
            user_id=user_id,
            event_type=event_type,
            location=location,
            recipient_ids=contact_ids,
        )

        return log
