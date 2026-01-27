"""
Pydantic schemas for ReminderSettings.

This module defines request/response schemas for reminder settings endpoints.
"""
from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReminderSettingsRequest(BaseModel):
    """Request schema for updating reminder settings."""

    reminder_hours_before: Optional[list[int]] = Field(
        default=None,
        description="Hours before deadline to send reminders (e.g., [48, 24, 12])",
        min_length=1,
        max_length=5,
    )
    quiet_hours_start: Optional[time] = Field(
        default=None,
        description="Start of quiet hours (HH:MM format)",
    )
    quiet_hours_end: Optional[time] = Field(
        default=None,
        description="End of quiet hours (HH:MM format)",
    )
    preferred_time: Optional[time] = Field(
        default=None,
        description="Preferred time for receiving reminders (HH:MM format)",
    )
    push_enabled: Optional[bool] = Field(
        default=None,
        description="Enable push notification reminders",
    )
    email_enabled: Optional[bool] = Field(
        default=None,
        description="Enable email reminders",
    )
    custom_message: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Custom reminder message (max 100 characters)",
    )


class ReminderSettingsResponse(BaseModel):
    """Response schema for reminder settings."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    reminder_hours_before: list[int]
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    preferred_time: Optional[time] = None
    push_enabled: bool
    email_enabled: bool
    custom_message: Optional[str] = None


class ReminderSettingsUpdateResponse(BaseModel):
    """Response schema after updating reminder settings."""

    message: str
    settings: ReminderSettingsResponse
