"""
Settings router for SoloCheck API.

This module defines the API endpoints for user settings,
including reminder customization.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.settings import service
from src.settings.schemas import (
    ReminderSettingsRequest,
    ReminderSettingsResponse,
    ReminderSettingsUpdateResponse,
)
from src.users.models import User

router = APIRouter()


@router.get(
    "/reminder",
    response_model=ReminderSettingsResponse,
    summary="Get reminder settings",
    description="Get the current user's reminder settings.",
)
def get_reminder_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReminderSettingsResponse:
    """Get the current user's reminder settings."""
    settings = service.get_reminder_settings(db, current_user.id)
    return ReminderSettingsResponse.model_validate(settings)


@router.put(
    "/reminder",
    response_model=ReminderSettingsUpdateResponse,
    summary="Update reminder settings",
    description="Update the current user's reminder settings.",
)
def update_reminder_settings(
    data: ReminderSettingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReminderSettingsUpdateResponse:
    """Update the current user's reminder settings."""
    settings = service.update_reminder_settings(db, current_user.id, data)
    return ReminderSettingsUpdateResponse(
        message="리마인더 설정이 업데이트되었습니다.",
        settings=ReminderSettingsResponse.model_validate(settings),
    )


@router.delete(
    "/reminder/quiet-hours",
    response_model=ReminderSettingsUpdateResponse,
    summary="Clear quiet hours",
    description="Clear the quiet hours settings.",
)
def clear_quiet_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReminderSettingsUpdateResponse:
    """Clear the quiet hours settings."""
    settings = service.clear_quiet_hours(db, current_user.id)
    return ReminderSettingsUpdateResponse(
        message="방해금지 시간이 해제되었습니다.",
        settings=ReminderSettingsResponse.model_validate(settings),
    )
