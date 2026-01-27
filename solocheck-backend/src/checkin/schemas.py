"""
Pydantic schemas for CheckIn-related requests and responses.

This module defines the validation schemas for check-in operations
including settings management and status queries.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CheckInSettingsRequest(BaseModel):
    """
    Request schema for updating check-in settings.

    Attributes:
        check_in_cycle: Check-in cycle in days (7, 14, or 30).
        grace_period: Grace period in hours (24, 48, or 72).
    """

    check_in_cycle: int = Field(
        ...,
        ge=7,
        le=30,
        description="Check-in cycle in days (7, 14, or 30)",
    )
    grace_period: int = Field(
        ...,
        ge=24,
        le=72,
        description="Grace period in hours (24, 48, or 72)",
    )


class CheckInSettingsResponse(BaseModel):
    """
    Response schema for check-in settings.

    Attributes:
        check_in_cycle: Current check-in cycle in days.
        grace_period: Current grace period in hours.
        next_check_in_due: Next expected check-in deadline.
    """

    model_config = ConfigDict(from_attributes=True)

    check_in_cycle: int
    grace_period: int
    next_check_in_due: Optional[datetime] = None


class CheckInStatusResponse(BaseModel):
    """
    Response schema for check-in status.

    Provides comprehensive status information including
    timing details and whether the user is overdue.

    Attributes:
        last_check_in: Last check-in timestamp.
        next_check_in_due: Next expected check-in deadline.
        days_remaining: Days remaining until next check-in.
        hours_remaining: Hours remaining until next check-in.
        is_overdue: Whether the user has missed their check-in deadline.
        check_in_cycle: Current check-in cycle in days.
        grace_period: Current grace period in hours.
    """

    model_config = ConfigDict(from_attributes=True)

    last_check_in: Optional[datetime] = None
    next_check_in_due: Optional[datetime] = None
    days_remaining: Optional[int] = None
    hours_remaining: Optional[int] = None
    is_overdue: bool
    check_in_cycle: int
    grace_period: int


class CheckInResponse(BaseModel):
    """
    Response schema for a successful check-in action.

    Attributes:
        id: Check-in log entry identifier.
        checked_at: Timestamp of the check-in.
        next_check_in_due: Next expected check-in deadline.
        message: Success message.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    checked_at: datetime
    next_check_in_due: datetime
    message: str = "Check-in successful"


class CheckInRequest(BaseModel):
    """
    Request schema for performing a check-in action.

    Attributes:
        method: Check-in method (app_open, button_click, push_response).
    """

    method: str = Field(
        default="button_click",
        description="Check-in method: 'app_open', 'button_click', or 'push_response'",
    )


class CheckInLogResponse(BaseModel):
    """
    Response schema for check-in log entry.

    Attributes:
        id: Log entry identifier.
        checked_at: Check-in timestamp.
        method: Check-in method (app_open, button_click, push_response).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    checked_at: datetime
    method: Optional[str] = None


class CheckInHistoryMeta(BaseModel):
    """
    Metadata schema for paginated check-in history.

    Attributes:
        page: Current page number.
        limit: Number of items per page.
        total: Total number of items.
        total_pages: Total number of pages.
    """

    page: int
    limit: int
    total: int
    total_pages: int


class CheckInHistoryResponse(BaseModel):
    """
    Response schema for paginated check-in history.

    Attributes:
        data: List of check-in log entries.
        meta: Pagination metadata.
    """

    data: list[CheckInLogResponse]
    meta: CheckInHistoryMeta


class QuickCheckInRequest(BaseModel):
    """
    Request schema for quick check-in via push notification or widget.

    Attributes:
        token: Session token from push notification.
        device_type: Source of check-in ('push', 'widget').
    """

    token: str = Field(
        ...,
        min_length=1,
        description="Session token from push notification",
    )
    device_type: str = Field(
        default="push",
        description="Source of check-in: 'push' or 'widget'",
    )


class QuickCheckInResponse(BaseModel):
    """
    Response schema for quick check-in.

    Attributes:
        success: Whether the check-in was successful.
        id: Check-in log entry identifier.
        checked_at: Timestamp of the check-in.
        next_check_in_due: Next expected check-in deadline.
        message: Status message.
    """

    model_config = ConfigDict(from_attributes=True)

    success: bool
    id: Optional[str] = None
    checked_at: Optional[datetime] = None
    next_check_in_due: Optional[datetime] = None
    message: str
