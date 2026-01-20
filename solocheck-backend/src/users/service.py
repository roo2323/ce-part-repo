"""
User service layer for business logic.

This module provides service functions for user-related operations
including retrieval, updates, and deletion.
"""
from typing import Optional

from sqlalchemy.orm import Session

from src.common.security import verify_password
from src.users.models import User
from src.users.schemas import UpdateUserRequest


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get a user by their ID.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        User or None: The user if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address.

    Args:
        db: Database session.
        email: The user's email address.

    Returns:
        User or None: The user if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: str, data: UpdateUserRequest) -> Optional[User]:
    """
    Update a user's profile information.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        data: Update data containing fields to modify.

    Returns:
        User or None: The updated user if found, None otherwise.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def update_fcm_token(db: Session, user_id: str, fcm_token: str) -> Optional[User]:
    """
    Update a user's FCM push notification token.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        fcm_token: The new FCM device token.

    Returns:
        User or None: The updated user if found, None otherwise.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    user.fcm_token = fcm_token
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: str, password: str) -> bool:
    """
    Delete a user account after password verification.

    This performs a soft delete by setting is_active to False.
    Related data (contacts, messages, etc.) will be handled by cascade.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        password: The user's password for verification.

    Returns:
        bool: True if deletion successful, False otherwise.

    Raises:
        ValueError: If password verification fails.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    # Verify password
    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid password")

    # Soft delete: deactivate the account
    user.is_active = False
    db.commit()
    return True


def hard_delete_user(db: Session, user_id: str) -> bool:
    """
    Permanently delete a user and all related data.

    WARNING: This is irreversible. Use with caution.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        bool: True if deletion successful, False otherwise.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True
