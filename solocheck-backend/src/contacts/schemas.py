"""
Pydantic schemas for emergency contacts API.

This module defines request/response schemas for contact-related operations
including creation, updates, and listing with validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactType(str, Enum):
    """Supported contact types."""

    EMAIL = "email"
    SMS = "sms"


class ContactCreateRequest(BaseModel):
    """Request schema for creating an emergency contact."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person's name",
    )
    contact_type: ContactType = Field(
        ...,
        description="Contact type: 'email' or 'sms'",
    )
    contact_value: str = Field(
        ...,
        max_length=255,
        description="Contact value (email address or phone number)",
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Contact priority (1 = highest, 3 = lowest)",
    )

    @field_validator("contact_value")
    @classmethod
    def validate_contact_value(cls, v: str, info) -> str:
        """Validate contact value based on contact type."""
        # Note: Full validation will be done in service layer
        # since we need access to contact_type field
        if not v or not v.strip():
            raise ValueError("Contact value cannot be empty")
        return v.strip()


class ContactUpdateRequest(BaseModel):
    """Request schema for updating an emergency contact."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Contact person's name",
    )
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=3,
        description="Contact priority (1 = highest, 3 = lowest)",
    )


class ContactResponse(BaseModel):
    """Response schema for a single emergency contact."""

    id: str = Field(..., description="Unique contact identifier")
    name: str = Field(..., description="Contact person's name")
    contact_type: str = Field(..., description="Contact type: 'email' or 'sms'")
    contact_value: str = Field(..., description="Contact value (email or phone)")
    priority: int = Field(..., description="Contact priority (1-3)")
    is_verified: bool = Field(..., description="Whether contact is verified")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    """Response schema for listing emergency contacts."""

    data: list[ContactResponse] = Field(
        ...,
        description="List of emergency contacts",
    )
    max_contacts: int = Field(
        default=3,
        description="Maximum allowed contacts",
    )
    current_count: int = Field(
        ...,
        description="Current number of contacts",
    )


class VerificationResponse(BaseModel):
    """Response schema for verification request."""

    message: str = Field(..., description="Status message")
    contact_id: str = Field(..., description="Contact ID")
    sent_to: str = Field(..., description="Verification sent to")
