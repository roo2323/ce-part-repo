"""
Pydantic schemas for SOS feature.

This module defines request/response schemas for SOS operations.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SOSTriggerRequest(BaseModel):
    """Request schema for triggering SOS."""

    location_lat: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude at trigger time",
    )
    location_lng: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude at trigger time",
    )


class SOSEventResponse(BaseModel):
    """Response schema for SOS event."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    triggered_at: datetime
    cancelled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    status: str
    created_at: datetime


class SOSTriggerResponse(BaseModel):
    """Response schema for SOS trigger action."""

    message: str
    event: SOSEventResponse
    countdown_seconds: int = Field(
        default=5,
        description="Seconds before notifications are sent",
    )


class SOSCancelResponse(BaseModel):
    """Response schema for SOS cancellation."""

    message: str
    event: SOSEventResponse


class SOSStatusResponse(BaseModel):
    """Response schema for SOS status check."""

    has_active_sos: bool
    active_event: Optional[SOSEventResponse] = None
