"""
User API router for FastAPI.

This module defines the API endpoints for user-related operations
including profile management and account deletion.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import CurrentActiveUser
from src.common.exceptions import UserNotFoundException, ValidationException
from src.database import get_db
from src.users.schemas import (
    DeleteUserRequest,
    UpdateFCMTokenRequest,
    UpdateUserRequest,
    UserResponse,
)
from src.users.service import delete_user, update_fcm_token, update_user


router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information.",
)
async def get_me(
    current_user: CurrentActiveUser,
) -> UserResponse:
    """
    Get the current authenticated user's profile.

    Args:
        current_user: The authenticated user from JWT token.

    Returns:
        UserResponse: The user's profile information.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the authenticated user's profile information.",
)
async def update_me(
    request: UpdateUserRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """
    Update the current authenticated user's profile.

    Args:
        request: Update data containing fields to modify.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        UserResponse: The updated user profile.

    Raises:
        UserNotFoundException: If user not found.
    """
    updated_user = update_user(db, current_user.id, request)
    if updated_user is None:
        raise UserNotFoundException()
    return UserResponse.model_validate(updated_user)


@router.put(
    "/me/fcm-token",
    response_model=UserResponse,
    summary="Update FCM token",
    description="Update the user's Firebase Cloud Messaging device token for push notifications.",
)
async def update_fcm_token_endpoint(
    request: UpdateFCMTokenRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """
    Update the current user's FCM push notification token.

    Args:
        request: Request containing the new FCM token.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        UserResponse: The updated user profile.

    Raises:
        UserNotFoundException: If user not found.
    """
    updated_user = update_fcm_token(db, current_user.id, request.fcm_token)
    if updated_user is None:
        raise UserNotFoundException()
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description="Permanently delete the authenticated user's account. Requires password confirmation.",
)
async def delete_me(
    request: DeleteUserRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete the current authenticated user's account.

    This performs a soft delete by deactivating the account.
    The user's password is required for confirmation.

    Args:
        request: Request containing password for verification.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Raises:
        ValidationException: If password is incorrect.
        UserNotFoundException: If user not found.
    """
    try:
        success = delete_user(db, current_user.id, request.password)
        if not success:
            raise UserNotFoundException()
    except ValueError as e:
        raise ValidationException(
            code="INVALID_PASSWORD",
            message=str(e),
        )
