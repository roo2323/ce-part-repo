"""
Pydantic schemas for Personal Messages.

This module defines the request and response schemas for personal message
operations including creation, update, and retrieval.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageUpdateRequest(BaseModel):
    """
    Request schema for updating a personal message.

    Attributes:
        content: The message content (max 2000 characters).
        is_enabled: Whether the message is enabled for delivery.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Personal message content (max 2000 characters)",
    )
    is_enabled: bool = Field(
        default=True,
        description="Whether the message is enabled for delivery",
    )


class MessageResponse(BaseModel):
    """
    Response schema for a personal message.

    Attributes:
        id: Unique identifier of the message.
        content: The decrypted message content.
        is_enabled: Whether the message is enabled.
        character_count: Current character count.
        max_characters: Maximum allowed characters (2000).
        updated_at: Last update timestamp.
    """

    id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the message",
    )
    content: Optional[str] = Field(
        default=None,
        description="The decrypted message content",
    )
    is_enabled: bool = Field(
        default=False,
        description="Whether the message is enabled for delivery",
    )
    character_count: int = Field(
        default=0,
        description="Current character count",
    )
    max_characters: int = Field(
        default=2000,
        description="Maximum allowed characters",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp",
    )

    model_config = {"from_attributes": True}


class MessageDeleteResponse(BaseModel):
    """
    Response schema for message deletion.

    Attributes:
        message: Confirmation message.
        deleted: Whether the deletion was successful.
    """

    message: str = Field(
        default="Message deleted successfully",
        description="Confirmation message",
    )
    deleted: bool = Field(
        default=True,
        description="Whether the deletion was successful",
    )
