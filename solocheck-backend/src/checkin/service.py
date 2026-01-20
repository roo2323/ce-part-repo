"""
CheckIn service layer for business logic.

This module provides service functions for check-in related operations
including settings management and status calculations.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.checkin.models import CheckInLog
from src.checkin.schemas import CheckInSettingsRequest, CheckInStatusResponse
from src.users.models import User


def calculate_next_check_in_due(
    last_check_in: Optional[datetime],
    cycle_days: int,
) -> Optional[datetime]:
    """
    Calculate the next check-in deadline.

    Args:
        last_check_in: The timestamp of the last check-in.
        cycle_days: The check-in cycle in days.

    Returns:
        datetime or None: The next check-in deadline, or None if no previous check-in.
    """
    if last_check_in is None:
        return None

    return last_check_in + timedelta(days=cycle_days)


def calculate_remaining_time(
    next_due: Optional[datetime],
) -> tuple[Optional[int], Optional[int]]:
    """
    Calculate remaining days and hours until next check-in.

    Args:
        next_due: The next check-in deadline.

    Returns:
        tuple: (days_remaining, hours_remaining) or (None, None) if no deadline.
    """
    if next_due is None:
        return None, None

    now = datetime.now(timezone.utc)

    # Ensure next_due is timezone-aware
    if next_due.tzinfo is None:
        next_due = next_due.replace(tzinfo=timezone.utc)

    remaining = next_due - now

    if remaining.total_seconds() <= 0:
        return 0, 0

    days = remaining.days
    hours = remaining.seconds // 3600

    return days, hours


def is_check_in_overdue(
    last_check_in: Optional[datetime],
    cycle_days: int,
    grace_hours: int,
) -> bool:
    """
    Determine if a check-in is overdue.

    A check-in is overdue if the current time exceeds:
    last_check_in + cycle_days + grace_hours

    Args:
        last_check_in: The timestamp of the last check-in.
        cycle_days: The check-in cycle in days.
        grace_hours: The grace period in hours.

    Returns:
        bool: True if overdue, False otherwise.
    """
    if last_check_in is None:
        # No previous check-in, not overdue yet
        return False

    now = datetime.now(timezone.utc)

    # Ensure last_check_in is timezone-aware
    if last_check_in.tzinfo is None:
        last_check_in = last_check_in.replace(tzinfo=timezone.utc)

    deadline = last_check_in + timedelta(days=cycle_days, hours=grace_hours)

    return now > deadline


def update_settings(
    db: Session,
    user_id: str,
    data: CheckInSettingsRequest,
) -> Optional[User]:
    """
    Update a user's check-in settings.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        data: Settings data containing cycle and grace period.

    Returns:
        User or None: The updated user if found, None otherwise.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    # Validate cycle values (should be 7, 14, or 30)
    valid_cycles = [7, 14, 30]
    if data.check_in_cycle not in valid_cycles:
        # Allow any value within range, but prefer standard values
        pass

    # Validate grace period values (should be 24, 48, or 72)
    valid_grace_periods = [24, 48, 72]
    if data.grace_period not in valid_grace_periods:
        # Allow any value within range, but prefer standard values
        pass

    user.check_in_cycle = data.check_in_cycle
    user.grace_period = data.grace_period

    db.commit()
    db.refresh(user)
    return user


def get_status(db: Session, user_id: str) -> Optional[CheckInStatusResponse]:
    """
    Get the check-in status for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        CheckInStatusResponse or None: The status if user found, None otherwise.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    next_due = calculate_next_check_in_due(user.last_check_in, user.check_in_cycle)
    days_remaining, hours_remaining = calculate_remaining_time(next_due)
    overdue = is_check_in_overdue(
        user.last_check_in,
        user.check_in_cycle,
        user.grace_period,
    )

    return CheckInStatusResponse(
        last_check_in=user.last_check_in,
        next_check_in_due=next_due,
        days_remaining=days_remaining,
        hours_remaining=hours_remaining,
        is_overdue=overdue,
        check_in_cycle=user.check_in_cycle,
        grace_period=user.grace_period,
    )


def get_settings(db: Session, user_id: str) -> Optional[dict]:
    """
    Get the check-in settings for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        dict or None: Settings dictionary if user found, None otherwise.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    next_due = calculate_next_check_in_due(user.last_check_in, user.check_in_cycle)

    return {
        "check_in_cycle": user.check_in_cycle,
        "grace_period": user.grace_period,
        "next_check_in_due": next_due,
    }


def create_check_in(
    db: Session,
    user_id: str,
    method: str = "button_click",
) -> Optional[tuple[CheckInLog, datetime]]:
    """
    Perform a check-in and record it.

    This function:
    1. Creates a new check_in_logs entry
    2. Updates the user's last_check_in timestamp
    3. Calculates and returns the next check-in deadline

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        method: Check-in method ('app_open', 'button_click', 'push_response').

    Returns:
        tuple or None: (CheckInLog, next_check_in_due) if successful, None if user not found.
    """
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    # Create the check-in timestamp
    checked_at = datetime.now(timezone.utc)

    # Create a new check-in log entry
    check_in_log = CheckInLog(
        user_id=user_id,
        checked_at=checked_at,
        method=method,
    )
    db.add(check_in_log)

    # Update user's last_check_in timestamp
    user.last_check_in = checked_at

    # Commit the transaction
    db.commit()
    db.refresh(check_in_log)
    db.refresh(user)

    # Calculate the next check-in deadline
    next_check_in_due = calculate_next_check_in_due(checked_at, user.check_in_cycle)

    return check_in_log, next_check_in_due


def get_check_in_history(
    db: Session,
    user_id: str,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[CheckInLog], int]:
    """
    Get paginated check-in history for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        page: Page number (1-indexed).
        limit: Number of items per page.

    Returns:
        tuple: (list of CheckInLog entries, total count).
    """
    # Calculate offset
    offset = (page - 1) * limit

    # Get total count
    total = db.query(CheckInLog).filter(CheckInLog.user_id == user_id).count()

    # Get paginated results, ordered by most recent first
    logs = (
        db.query(CheckInLog)
        .filter(CheckInLog.user_id == user_id)
        .order_by(CheckInLog.checked_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return logs, total
