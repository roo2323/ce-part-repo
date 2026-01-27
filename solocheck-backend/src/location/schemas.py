"""
Pydantic schemas for Location endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LocationConsentRequest(BaseModel):
    """Schema for updating location consent."""
    consent: bool


class LocationConsentResponse(BaseModel):
    """Schema for location consent response."""
    location_consent: bool
    location_consent_at: Optional[datetime] = None
    message: str


class LocationData(BaseModel):
    """Schema for location data."""
    lat: float
    lng: float


class LocationSharingLogResponse(BaseModel):
    """Schema for location sharing log response."""
    id: str
    user_id: str
    event_type: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    recipient_ids: Optional[list[str]] = None
    shared_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationSharingHistoryResponse(BaseModel):
    """Schema for location sharing history response."""
    logs: list[LocationSharingLogResponse]
    total: int
