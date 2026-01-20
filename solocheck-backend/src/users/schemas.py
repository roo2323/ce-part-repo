"""
Pydantic schemas for User-related requests and responses.

This module defines the validation schemas for user operations
including profile retrieval, updates, and account deletion.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """
    Response schema for user information.

    Attributes:
        id: Unique user identifier.
        email: User's email address.
        nickname: User's display nickname.
        check_in_cycle: Check-in cycle in days (7, 14, or 30).
        grace_period: Grace period in hours (24, 48, or 72).
        last_check_in: Last check-in timestamp.
        is_active: Whether the user account is active.
        created_at: Account creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    nickname: Optional[str] = None
    check_in_cycle: int
    grace_period: int
    last_check_in: Optional[datetime] = None
    is_active: bool
    created_at: datetime


class UpdateUserRequest(BaseModel):
    """
    Request schema for updating user profile.

    Attributes:
        nickname: New nickname (optional).
    """

    nickname: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's display nickname",
    )


class UpdateFCMTokenRequest(BaseModel):
    """
    Request schema for updating FCM push notification token.

    Attributes:
        fcm_token: Firebase Cloud Messaging device token.
    """

    fcm_token: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Firebase Cloud Messaging device token",
    )


class DeleteUserRequest(BaseModel):
    """
    Request schema for account deletion.

    Requires password confirmation for security.

    Attributes:
        password: Current password for verification.
    """

    password: str = Field(
        ...,
        min_length=1,
        description="Current password for verification",
    )


class UserProfileResponse(BaseModel):
    """
    Detailed response schema for user profile.

    Extends UserResponse with additional computed fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    nickname: Optional[str] = None
    check_in_cycle: int
    grace_period: int
    last_check_in: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
