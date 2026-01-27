"""
Location API router for SoloCheck.

Endpoints for location consent and sharing history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.users.models import User
from src.location.schemas import (
    LocationConsentRequest,
    LocationConsentResponse,
    LocationSharingHistoryResponse,
    LocationSharingLogResponse,
)
from src.location.service import LocationService

router = APIRouter()


@router.get(
    "/consent",
    response_model=LocationConsentResponse,
    summary="Get location consent status",
    description="Get the current user's location consent status.",
)
def get_location_consent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get location consent status."""
    consent, consent_at = LocationService.get_location_consent(
        db, current_user.id
    )
    return LocationConsentResponse(
        location_consent=consent,
        location_consent_at=consent_at,
        message="위치정보 동의 상태입니다." if consent else "위치정보 동의가 필요합니다.",
    )


@router.post(
    "/consent",
    response_model=LocationConsentResponse,
    summary="Update location consent",
    description="Update the current user's location consent.",
)
def update_location_consent(
    data: LocationConsentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update location consent."""
    consent, consent_at = LocationService.update_location_consent(
        db, current_user.id, data.consent
    )
    if consent:
        message = "위치정보 공유에 동의하셨습니다."
    else:
        message = "위치정보 공유 동의가 철회되었습니다."

    return LocationConsentResponse(
        location_consent=consent,
        location_consent_at=consent_at,
        message=message,
    )


@router.get(
    "/history",
    response_model=LocationSharingHistoryResponse,
    summary="Get location sharing history",
    description="Get the history of location sharing events.",
)
def get_location_sharing_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get location sharing history."""
    logs = LocationService.get_location_sharing_history(
        db, current_user.id, limit
    )
    return LocationSharingHistoryResponse(
        logs=[
            LocationSharingLogResponse(
                id=log.id,
                user_id=log.user_id,
                event_type=log.event_type,
                location_lat=float(log.location_lat) if log.location_lat else None,
                location_lng=float(log.location_lng) if log.location_lng else None,
                recipient_ids=log.recipient_ids,
                shared_at=log.shared_at,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=len(logs),
    )
