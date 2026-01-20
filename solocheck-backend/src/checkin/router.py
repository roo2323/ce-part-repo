"""
CheckIn API router for FastAPI.

This module defines the API endpoints for check-in related operations
including status queries and settings management.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import CurrentActiveUser
from src.checkin.schemas import (
    CheckInHistoryMeta,
    CheckInHistoryResponse,
    CheckInLogResponse,
    CheckInRequest,
    CheckInResponse,
    CheckInSettingsRequest,
    CheckInSettingsResponse,
    CheckInStatusResponse,
)
from src.checkin.service import (
    create_check_in,
    get_check_in_history,
    get_settings,
    get_status,
    update_settings,
)
from src.common.exceptions import UserNotFoundException
from src.database import get_db


router = APIRouter()


@router.get(
    "/status",
    response_model=CheckInStatusResponse,
    summary="Get check-in status",
    description="Get the current check-in status including timing and overdue information.",
)
async def get_checkin_status(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> CheckInStatusResponse:
    """
    Get the current user's check-in status.

    Returns comprehensive status information including:
    - Last check-in timestamp
    - Next check-in deadline
    - Remaining time
    - Whether the user is overdue

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        CheckInStatusResponse: The check-in status information.

    Raises:
        UserNotFoundException: If user not found.
    """
    status = get_status(db, current_user.id)
    if status is None:
        raise UserNotFoundException()
    return status


@router.get(
    "/settings",
    response_model=CheckInSettingsResponse,
    summary="Get check-in settings",
    description="Get the current check-in cycle and grace period settings.",
)
async def get_checkin_settings(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> CheckInSettingsResponse:
    """
    Get the current user's check-in settings.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        CheckInSettingsResponse: The check-in settings.

    Raises:
        UserNotFoundException: If user not found.
    """
    settings = get_settings(db, current_user.id)
    if settings is None:
        raise UserNotFoundException()
    return CheckInSettingsResponse(**settings)


@router.put(
    "/settings",
    response_model=CheckInSettingsResponse,
    summary="Update check-in settings",
    description="Update the check-in cycle (7, 14, or 30 days) and grace period (24, 48, or 72 hours).",
)
async def update_checkin_settings(
    request: CheckInSettingsRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> CheckInSettingsResponse:
    """
    Update the current user's check-in settings.

    Valid values:
    - check_in_cycle: 7, 14, or 30 days
    - grace_period: 24, 48, or 72 hours

    Args:
        request: Settings data containing cycle and grace period.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        CheckInSettingsResponse: The updated check-in settings.

    Raises:
        UserNotFoundException: If user not found.
    """
    user = update_settings(db, current_user.id, request)
    if user is None:
        raise UserNotFoundException()

    settings = get_settings(db, current_user.id)
    return CheckInSettingsResponse(**settings)


@router.post(
    "",
    response_model=CheckInResponse,
    summary="Perform check-in",
    description="Record a check-in and update the user's last check-in timestamp.",
)
async def perform_checkin(
    request: CheckInRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> CheckInResponse:
    """
    Perform a check-in for the current user.

    This endpoint:
    1. Creates a new check-in log entry
    2. Updates the user's last_check_in timestamp
    3. Returns the check-in confirmation with next deadline

    Args:
        request: Check-in request with method type.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        CheckInResponse: Check-in confirmation with next deadline.

    Raises:
        UserNotFoundException: If user not found.
    """
    result = create_check_in(db, current_user.id, request.method)
    if result is None:
        raise UserNotFoundException()

    check_in_log, next_check_in_due = result

    return CheckInResponse(
        id=check_in_log.id,
        checked_at=check_in_log.checked_at,
        next_check_in_due=next_check_in_due,
        message="Check-in successful",
    )


@router.get(
    "/history",
    response_model=CheckInHistoryResponse,
    summary="Get check-in history",
    description="Get paginated check-in history for the current user.",
)
async def get_checkin_history(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
    page: int = 1,
    limit: int = 20,
) -> CheckInHistoryResponse:
    """
    Get the current user's check-in history with pagination.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.
        page: Page number (1-indexed, default 1).
        limit: Number of items per page (default 20).

    Returns:
        CheckInHistoryResponse: Paginated check-in history with metadata.
    """
    # Ensure valid pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    logs, total = get_check_in_history(db, current_user.id, page, limit)

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 0

    # Convert to response format
    log_responses = [
        CheckInLogResponse(
            id=log.id,
            checked_at=log.checked_at,
            method=log.method,
        )
        for log in logs
    ]

    return CheckInHistoryResponse(
        data=log_responses,
        meta=CheckInHistoryMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )
