"""
Pydantic schemas for authentication endpoints.

This module defines request and response schemas for
registration, login, token refresh, and password reset.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User's password (minimum 8 characters)",
        examples=["securePassword123"],
    )
    nickname: str | None = Field(
        default=None,
        max_length=100,
        description="User's display name (optional)",
        examples=["홍길동"],
    )


class LoginRequest(BaseModel):
    """Schema for user login request (JSON body)."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="User's password",
        examples=["securePassword123"],
    )


class TokenResponse(BaseModel):
    """Schema for token response after successful authentication."""

    access_token: str = Field(
        ...,
        description="JWT access token",
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
    )


class RegisterResponse(BaseModel):
    """Schema for successful registration response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="User's unique identifier",
    )
    email: str = Field(
        ...,
        description="User's email address",
    )
    nickname: str | None = Field(
        default=None,
        description="User's display name",
    )
    access_token: str = Field(
        ...,
        description="JWT access token",
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
    )


class RefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
    )


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""

    email: EmailStr = Field(
        ...,
        description="User's email address for password reset",
        examples=["user@example.com"],
    )


class ForgotPasswordResponse(BaseModel):
    """Schema for forgot password response."""

    message: str = Field(
        default="If the email exists, a password reset link has been sent.",
        description="Response message",
    )


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="User's unique identifier",
    )
    email: str = Field(
        ...,
        description="User's email address",
    )
    nickname: str | None = Field(
        default=None,
        description="User's display name",
    )
    is_active: bool = Field(
        ...,
        description="Whether the user account is active",
    )


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(
        ...,
        description="Current password",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)",
    )


class ChangePasswordResponse(BaseModel):
    """Schema for password change response."""

    message: str = Field(
        default="비밀번호가 변경되었습니다.",
        description="Response message",
    )
