"""
Custom exceptions for SoloCheck.

This module defines the exception hierarchy used throughout the application
for consistent error handling and response formatting.
"""
from typing import Any

from fastapi import HTTPException, status


class SoloCheckException(HTTPException):
    """
    Base exception for all SoloCheck application errors.

    Provides a consistent structure for error responses with
    error codes, messages, and HTTP status codes.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            code: A unique error code for client-side handling.
            message: Human-readable error message.
            status_code: HTTP status code (default 400).
            headers: Optional HTTP headers to include in response.
        """
        self.code = code
        self.message = message
        detail: dict[str, Any] = {
            "code": code,
            "message": message,
        }
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthException(SoloCheckException):
    """Exception for authentication-related errors."""

    def __init__(
        self,
        code: str = "AUTH_ERROR",
        message: str = "Authentication failed",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize authentication exception."""
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(code=code, message=message, status_code=status_code, headers=headers)


class InvalidCredentialsException(AuthException):
    """Exception for invalid email or password."""

    def __init__(self) -> None:
        """Initialize invalid credentials exception."""
        super().__init__(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password",
        )


class InvalidTokenException(AuthException):
    """Exception for invalid or expired tokens."""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        """Initialize invalid token exception."""
        super().__init__(
            code="INVALID_TOKEN",
            message=message,
        )


class TokenExpiredException(AuthException):
    """Exception for expired tokens."""

    def __init__(self) -> None:
        """Initialize token expired exception."""
        super().__init__(
            code="TOKEN_EXPIRED",
            message="Token has expired",
        )


class InactiveUserException(AuthException):
    """Exception for inactive user accounts."""

    def __init__(self) -> None:
        """Initialize inactive user exception."""
        super().__init__(
            code="INACTIVE_USER",
            message="User account is inactive",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(SoloCheckException):
    """Exception for resources not found."""

    def __init__(
        self,
        code: str = "NOT_FOUND",
        message: str = "Resource not found",
    ) -> None:
        """Initialize not found exception."""
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserNotFoundException(NotFoundException):
    """Exception for user not found."""

    def __init__(self) -> None:
        """Initialize user not found exception."""
        super().__init__(
            code="USER_NOT_FOUND",
            message="User not found",
        )


class ValidationException(SoloCheckException):
    """Exception for validation errors."""

    def __init__(
        self,
        code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> None:
        """Initialize validation exception."""
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class DuplicateEmailException(SoloCheckException):
    """Exception for duplicate email registration."""

    def __init__(self) -> None:
        """Initialize duplicate email exception."""
        super().__init__(
            code="DUPLICATE_EMAIL",
            message="Email already registered",
            status_code=status.HTTP_409_CONFLICT,
        )


class PermissionDeniedException(SoloCheckException):
    """Exception for permission denied errors."""

    def __init__(
        self,
        code: str = "PERMISSION_DENIED",
        message: str = "Permission denied",
    ) -> None:
        """Initialize permission denied exception."""
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class MessageTooLongException(SoloCheckException):
    """Exception for message exceeding maximum character limit."""

    def __init__(self) -> None:
        """Initialize message too long exception."""
        super().__init__(
            code="MESSAGE001",
            message="메시지는 2000자를 초과할 수 없습니다",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MessageNotFoundException(NotFoundException):
    """Exception for personal message not found."""

    def __init__(self) -> None:
        """Initialize message not found exception."""
        super().__init__(
            code="MESSAGE_NOT_FOUND",
            message="Personal message not found",
        )


class MessageDecryptionException(SoloCheckException):
    """Exception for message decryption failure."""

    def __init__(self) -> None:
        """Initialize decryption exception."""
        super().__init__(
            code="MESSAGE002",
            message="Failed to decrypt message",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Contact-related exceptions
class MaxContactsExceededException(SoloCheckException):
    """Exception for exceeding maximum contacts limit."""

    def __init__(self) -> None:
        """Initialize max contacts exceeded exception."""
        super().__init__(
            code="CONTACT001",
            message="비상연락처는 최대 3명까지 등록 가능합니다",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DuplicateContactException(SoloCheckException):
    """Exception for duplicate contact registration."""

    def __init__(self) -> None:
        """Initialize duplicate contact exception."""
        super().__init__(
            code="CONTACT002",
            message="이미 등록된 연락처입니다",
            status_code=status.HTTP_409_CONFLICT,
        )
