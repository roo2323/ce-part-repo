"""
SOS service layer for business logic.

This module provides service functions for SOS emergency operations.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.contacts.service import get_active_contacts
from src.sos.models import (
    SOSEvent,
    SOS_STATUS_TRIGGERED,
    SOS_STATUS_CANCELLED,
    SOS_STATUS_SENT,
)
from src.users.models import User


# SOS countdown delay before sending notifications (seconds)
SOS_COUNTDOWN_SECONDS = 5


def trigger_sos(
    db: Session,
    user_id: str,
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
) -> Optional[SOSEvent]:
    """
    Trigger an SOS event.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        location_lat: Optional latitude.
        location_lng: Optional longitude.

    Returns:
        SOSEvent or None: The created event if successful.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    # Create SOS event
    sos_event = SOSEvent(
        user_id=user_id,
        triggered_at=datetime.now(timezone.utc),
        location_lat=Decimal(str(location_lat)) if location_lat is not None else None,
        location_lng=Decimal(str(location_lng)) if location_lng is not None else None,
        status=SOS_STATUS_TRIGGERED,
    )

    db.add(sos_event)
    db.commit()
    db.refresh(sos_event)

    return sos_event


def cancel_sos(
    db: Session,
    user_id: str,
    sos_id: str,
) -> Optional[SOSEvent]:
    """
    Cancel an active SOS event.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        sos_id: The SOS event identifier.

    Returns:
        SOSEvent or None: The cancelled event if found and cancelled.
    """
    sos_event = (
        db.query(SOSEvent)
        .filter(
            SOSEvent.id == sos_id,
            SOSEvent.user_id == user_id,
            SOSEvent.status == SOS_STATUS_TRIGGERED,
        )
        .first()
    )

    if sos_event is None:
        return None

    sos_event.status = SOS_STATUS_CANCELLED
    sos_event.cancelled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(sos_event)

    return sos_event


def get_active_sos(db: Session, user_id: str) -> Optional[SOSEvent]:
    """
    Get the active SOS event for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        SOSEvent or None: The active event if exists.
    """
    return (
        db.query(SOSEvent)
        .filter(
            SOSEvent.user_id == user_id,
            SOSEvent.status == SOS_STATUS_TRIGGERED,
        )
        .order_by(SOSEvent.triggered_at.desc())
        .first()
    )


def get_sos_event(db: Session, sos_id: str) -> Optional[SOSEvent]:
    """
    Get an SOS event by ID.

    Args:
        db: Database session.
        sos_id: The SOS event identifier.

    Returns:
        SOSEvent or None: The event if found.
    """
    return db.query(SOSEvent).filter(SOSEvent.id == sos_id).first()


def mark_sos_sent(db: Session, sos_id: str) -> Optional[SOSEvent]:
    """
    Mark an SOS event as sent.

    Args:
        db: Database session.
        sos_id: The SOS event identifier.

    Returns:
        SOSEvent or None: The updated event if found.
    """
    sos_event = db.query(SOSEvent).filter(SOSEvent.id == sos_id).first()
    if sos_event is None:
        return None

    sos_event.status = SOS_STATUS_SENT
    sos_event.sent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(sos_event)

    return sos_event


def is_sos_still_active(db: Session, sos_id: str) -> bool:
    """
    Check if an SOS event is still active (not cancelled).

    Args:
        db: Database session.
        sos_id: The SOS event identifier.

    Returns:
        bool: True if still triggered, False otherwise.
    """
    sos_event = db.query(SOSEvent).filter(SOSEvent.id == sos_id).first()
    if sos_event is None:
        return False

    return sos_event.status == SOS_STATUS_TRIGGERED


def get_user_sos_history(
    db: Session,
    user_id: str,
    limit: int = 10,
) -> list[SOSEvent]:
    """
    Get SOS event history for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        limit: Maximum number of events to return.

    Returns:
        list[SOSEvent]: List of recent SOS events.
    """
    return (
        db.query(SOSEvent)
        .filter(SOSEvent.user_id == user_id)
        .order_by(SOSEvent.triggered_at.desc())
        .limit(limit)
        .all()
    )
