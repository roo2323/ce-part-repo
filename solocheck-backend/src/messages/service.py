"""
Personal Message service layer for business logic.

This module provides service functions for personal message operations
including CRUD operations with encryption support.
"""
from typing import Optional

from cryptography.fernet import InvalidToken
from sqlalchemy.orm import Session

from src.common.encryption import decrypt_message, encrypt_message
from src.common.exceptions import (
    MessageDecryptionException,
    MessageTooLongException,
)
from src.messages.models import PersonalMessage
from src.messages.schemas import MessageResponse

# Maximum characters allowed for personal messages
MAX_CHARACTERS = 2000


def get_message(db: Session, user_id: str) -> Optional[MessageResponse]:
    """
    Retrieve a user's personal message.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        MessageResponse or None: The decrypted message response if found.

    Raises:
        MessageDecryptionException: If decryption fails.
    """
    message = db.query(PersonalMessage).filter(
        PersonalMessage.user_id == user_id
    ).first()

    if message is None:
        return None

    try:
        decrypted_content = decrypt_message(message.content)
    except InvalidToken:
        raise MessageDecryptionException()

    return MessageResponse(
        id=message.id,
        content=decrypted_content,
        is_enabled=message.is_enabled,
        character_count=len(decrypted_content),
        max_characters=MAX_CHARACTERS,
        updated_at=message.updated_at,
    )


def save_message(
    db: Session,
    user_id: str,
    content: str,
    is_enabled: bool = True,
) -> MessageResponse:
    """
    Save or update a user's personal message.

    If a message already exists for the user, it will be updated.
    Otherwise, a new message will be created.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        content: The plaintext message content.
        is_enabled: Whether the message is enabled for delivery.

    Returns:
        MessageResponse: The saved message response.

    Raises:
        MessageTooLongException: If content exceeds MAX_CHARACTERS.
    """
    # Validate content length
    if len(content) > MAX_CHARACTERS:
        raise MessageTooLongException()

    # Encrypt the content
    encrypted_content = encrypt_message(content)

    # Check if message already exists
    existing_message = db.query(PersonalMessage).filter(
        PersonalMessage.user_id == user_id
    ).first()

    if existing_message:
        # Update existing message
        existing_message.content = encrypted_content
        existing_message.is_enabled = is_enabled
        db.commit()
        db.refresh(existing_message)
        message = existing_message
    else:
        # Create new message
        message = PersonalMessage(
            user_id=user_id,
            content=encrypted_content,
            is_enabled=is_enabled,
        )
        db.add(message)
        db.commit()
        db.refresh(message)

    return MessageResponse(
        id=message.id,
        content=content,  # Return original content, not encrypted
        is_enabled=message.is_enabled,
        character_count=len(content),
        max_characters=MAX_CHARACTERS,
        updated_at=message.updated_at,
    )


def delete_message(db: Session, user_id: str) -> bool:
    """
    Delete a user's personal message.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        bool: True if a message was deleted, False if no message existed.
    """
    message = db.query(PersonalMessage).filter(
        PersonalMessage.user_id == user_id
    ).first()

    if message is None:
        return False

    db.delete(message)
    db.commit()
    return True


def get_message_for_notification(db: Session, user_id: str) -> Optional[str]:
    """
    Get the decrypted message content for notification purposes.

    This function is intended for use by the notification service
    when sending messages to emergency contacts.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        str or None: The decrypted message content if enabled, None otherwise.

    Raises:
        MessageDecryptionException: If decryption fails.
    """
    message = db.query(PersonalMessage).filter(
        PersonalMessage.user_id == user_id,
        PersonalMessage.is_enabled == True,  # noqa: E712
    ).first()

    if message is None:
        return None

    try:
        return decrypt_message(message.content)
    except InvalidToken:
        raise MessageDecryptionException()
