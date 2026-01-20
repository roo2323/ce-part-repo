"""
Personal Message API router for FastAPI.

This module defines the API endpoints for personal message operations
including CRUD operations with encryption.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.messages.schemas import (
    MessageDeleteResponse,
    MessageResponse,
    MessageUpdateRequest,
)
from src.messages.service import (
    delete_message,
    get_message,
    save_message,
    MAX_CHARACTERS,
)

router = APIRouter()


@router.get(
    "",
    response_model=MessageResponse,
    summary="Get personal message",
    description="Retrieve the current user's personal message (decrypted).",
)
async def get_personal_message(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """
    Get the current user's personal message.

    If no message exists, returns an empty response with default values.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        MessageResponse: The decrypted personal message or empty response.
    """
    message = get_message(db, current_user.id)

    if message is None:
        # Return empty response if no message exists
        return MessageResponse(
            id=None,
            content=None,
            is_enabled=False,
            character_count=0,
            max_characters=MAX_CHARACTERS,
            updated_at=None,
        )

    return message


@router.put(
    "",
    response_model=MessageResponse,
    summary="Save personal message",
    description="Create or update the current user's personal message.",
)
async def save_personal_message(
    request: MessageUpdateRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """
    Save or update the current user's personal message.

    The message will be encrypted before storage.

    Args:
        request: Message data containing content and enabled status.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        MessageResponse: The saved personal message.

    Raises:
        MessageTooLongException: If content exceeds 2000 characters.
    """
    return save_message(
        db=db,
        user_id=current_user.id,
        content=request.content,
        is_enabled=request.is_enabled,
    )


@router.delete(
    "",
    response_model=MessageDeleteResponse,
    summary="Delete personal message",
    description="Delete the current user's personal message.",
)
async def delete_personal_message(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> MessageDeleteResponse:
    """
    Delete the current user's personal message.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        MessageDeleteResponse: Deletion confirmation.
    """
    deleted = delete_message(db, current_user.id)

    if deleted:
        return MessageDeleteResponse(
            message="Message deleted successfully",
            deleted=True,
        )
    else:
        return MessageDeleteResponse(
            message="No message to delete",
            deleted=False,
        )
