"""
SOS API router for FastAPI.

This module defines the API endpoints for SOS emergency operations.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import CurrentActiveUser
from src.common.exceptions import NotFoundException
from src.database import get_db
from src.sos.schemas import (
    SOSCancelResponse,
    SOSEventResponse,
    SOSStatusResponse,
    SOSTriggerRequest,
    SOSTriggerResponse,
)
from src.sos.service import (
    SOS_COUNTDOWN_SECONDS,
    cancel_sos,
    get_active_sos,
    trigger_sos,
)

router = APIRouter()


class SOSNotFoundException(NotFoundException):
    """Exception for SOS event not found."""

    def __init__(self) -> None:
        """Initialize SOS not found exception."""
        super().__init__(
            code="SOS_NOT_FOUND",
            message="활성화된 SOS 이벤트가 없습니다.",
        )


@router.post(
    "/trigger",
    response_model=SOSTriggerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger SOS",
    description="Trigger an SOS emergency alert. Notifications will be sent after countdown.",
)
async def trigger_sos_alert(
    request: SOSTriggerRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> SOSTriggerResponse:
    """
    Trigger an SOS emergency alert.

    This starts a countdown (default 5 seconds) before notifications
    are sent to emergency contacts. User can cancel during countdown.

    Args:
        request: SOS trigger request with optional location.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        SOSTriggerResponse: SOS event with countdown information.
    """
    sos_event = trigger_sos(
        db=db,
        user_id=current_user.id,
        location_lat=request.location_lat,
        location_lng=request.location_lng,
    )

    # Schedule the delayed notification task
    from src.scheduler.tasks import send_sos_alerts_delayed

    send_sos_alerts_delayed.apply_async(
        args=[sos_event.id],
        countdown=SOS_COUNTDOWN_SECONDS,
    )

    return SOSTriggerResponse(
        message="SOS가 발동되었습니다. 5초 후 비상연락처에 알림이 발송됩니다.",
        event=SOSEventResponse.model_validate(sos_event),
        countdown_seconds=SOS_COUNTDOWN_SECONDS,
    )


@router.post(
    "/{sos_id}/cancel",
    response_model=SOSCancelResponse,
    summary="Cancel SOS",
    description="Cancel an active SOS alert before notifications are sent.",
)
async def cancel_sos_alert(
    sos_id: str,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> SOSCancelResponse:
    """
    Cancel an active SOS alert.

    Must be called before the countdown expires to prevent
    notifications from being sent.

    Args:
        sos_id: The SOS event identifier.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        SOSCancelResponse: Cancellation confirmation.

    Raises:
        SOSNotFoundException: If SOS event not found or already processed.
    """
    sos_event = cancel_sos(db, current_user.id, sos_id)
    if sos_event is None:
        raise SOSNotFoundException()

    return SOSCancelResponse(
        message="SOS가 취소되었습니다.",
        event=SOSEventResponse.model_validate(sos_event),
    )


@router.get(
    "/status",
    response_model=SOSStatusResponse,
    summary="Get SOS status",
    description="Check if there's an active SOS alert.",
)
async def get_sos_status(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> SOSStatusResponse:
    """
    Get the current SOS status for the user.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        SOSStatusResponse: Current SOS status.
    """
    active_sos = get_active_sos(db, current_user.id)

    return SOSStatusResponse(
        has_active_sos=active_sos is not None,
        active_event=(
            SOSEventResponse.model_validate(active_sos) if active_sos else None
        ),
    )
