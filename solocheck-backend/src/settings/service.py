"""
ReminderSettings service layer for business logic.

This module provides service functions for reminder settings operations.
"""
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.settings.models import ReminderSettings
from src.settings.schemas import ReminderSettingsRequest
from src.users.models import User


def get_reminder_settings(db: Session, user_id: str) -> Optional[ReminderSettings]:
    """
    Get reminder settings for a user.

    If settings don't exist, creates default settings.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        ReminderSettings: The user's reminder settings.
    """
    settings = (
        db.query(ReminderSettings)
        .filter(ReminderSettings.user_id == user_id)
        .first()
    )

    if settings is None:
        # Create default settings
        settings = ReminderSettings(
            user_id=user_id,
            reminder_hours_before=[48, 24, 12],
            push_enabled=True,
            email_enabled=False,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def update_reminder_settings(
    db: Session,
    user_id: str,
    data: ReminderSettingsRequest,
) -> Optional[ReminderSettings]:
    """
    Update reminder settings for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        data: Settings data to update.

    Returns:
        ReminderSettings or None: Updated settings if successful.
    """
    # Ensure settings exist
    settings = get_reminder_settings(db, user_id)
    if settings is None:
        return None

    # Update only provided fields
    if data.reminder_hours_before is not None:
        # Validate hours (must be positive and reasonable)
        valid_hours = [h for h in data.reminder_hours_before if 1 <= h <= 168]
        if valid_hours:
            settings.reminder_hours_before = sorted(valid_hours, reverse=True)

    if data.quiet_hours_start is not None:
        settings.quiet_hours_start = data.quiet_hours_start

    if data.quiet_hours_end is not None:
        settings.quiet_hours_end = data.quiet_hours_end

    if data.preferred_time is not None:
        settings.preferred_time = data.preferred_time

    if data.push_enabled is not None:
        settings.push_enabled = data.push_enabled

    if data.email_enabled is not None:
        settings.email_enabled = data.email_enabled

    if data.custom_message is not None:
        settings.custom_message = data.custom_message[:100] if data.custom_message else None

    db.commit()
    db.refresh(settings)
    return settings


def clear_quiet_hours(db: Session, user_id: str) -> Optional[ReminderSettings]:
    """
    Clear quiet hours settings for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        ReminderSettings or None: Updated settings if successful.
    """
    settings = get_reminder_settings(db, user_id)
    if settings is None:
        return None

    settings.quiet_hours_start = None
    settings.quiet_hours_end = None

    db.commit()
    db.refresh(settings)
    return settings


def is_in_quiet_hours(
    settings: ReminderSettings,
    current_time: Optional[time] = None,
) -> bool:
    """
    Check if the current time is within quiet hours.

    Args:
        settings: User's reminder settings.
        current_time: Time to check (defaults to now).

    Returns:
        bool: True if in quiet hours, False otherwise.
    """
    if settings.quiet_hours_start is None or settings.quiet_hours_end is None:
        return False

    if current_time is None:
        current_time = datetime.now(timezone.utc).time()

    start = settings.quiet_hours_start
    end = settings.quiet_hours_end

    # Handle overnight quiet hours (e.g., 22:00 to 08:00)
    if start <= end:
        # Same day range (e.g., 09:00 to 17:00)
        return start <= current_time <= end
    else:
        # Overnight range (e.g., 22:00 to 08:00)
        return current_time >= start or current_time <= end


def should_send_reminder(
    db: Session,
    user: User,
    hours_until_deadline: int,
) -> tuple[bool, Optional[str]]:
    """
    Determine if a reminder should be sent to a user.

    Args:
        db: Database session.
        user: The user to check.
        hours_until_deadline: Hours remaining until check-in deadline.

    Returns:
        tuple: (should_send, custom_message)
    """
    settings = get_reminder_settings(db, user.id)
    if settings is None:
        return False, None

    # Check if push notifications are enabled
    if not settings.push_enabled:
        return False, None

    # Check quiet hours
    if is_in_quiet_hours(settings):
        return False, None

    # Check if this hour threshold is in the user's settings
    for threshold in settings.reminder_hours_before:
        # Allow some tolerance (within 3 hours of the threshold)
        if abs(hours_until_deadline - threshold) <= 3:
            return True, settings.custom_message

    return False, None


def get_active_reminder_hours(settings: ReminderSettings) -> list[int]:
    """
    Get the list of hours before deadline when reminders should be sent.

    Args:
        settings: User's reminder settings.

    Returns:
        list[int]: List of hour thresholds.
    """
    if settings.reminder_hours_before:
        return sorted(settings.reminder_hours_before, reverse=True)
    return [48, 24, 12]  # Default
