"""
Contact service layer for business logic.

This module provides service functions for emergency contact operations
including CRUD operations, verification, consent management, and business rule enforcement.
"""
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.contacts.models import (
    EmergencyContact,
    CONSENT_STATUS_PENDING,
    CONSENT_STATUS_APPROVED,
    CONSENT_STATUS_REJECTED,
    CONSENT_STATUS_EXPIRED,
)
from src.contacts.schemas import ContactCreateRequest, ContactType, ContactUpdateRequest

# Maximum number of emergency contacts per user
MAX_CONTACTS = 3

# Consent token validity period (7 days)
CONSENT_TOKEN_VALIDITY_DAYS = 7


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Remove common separators for validation
    cleaned = re.sub(r"[\s\-\.\(\)]", "", phone)
    # Korean phone number or international format
    pattern = r"^(\+?82|0)?1[0-9]{8,9}$"
    return bool(re.match(pattern, cleaned))


def get_contacts(db: Session, user_id: str) -> list[EmergencyContact]:
    """
    Get all emergency contacts for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        list[EmergencyContact]: List of contacts ordered by priority.
    """
    return (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == user_id)
        .order_by(EmergencyContact.priority)
        .all()
    )


def get_contact_by_id(
    db: Session,
    user_id: str,
    contact_id: str,
) -> Optional[EmergencyContact]:
    """
    Get a specific contact by ID for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.

    Returns:
        EmergencyContact or None: The contact if found, None otherwise.
    """
    return (
        db.query(EmergencyContact)
        .filter(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == user_id,
        )
        .first()
    )


def get_contact_count(db: Session, user_id: str) -> int:
    """
    Get the number of contacts for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        int: Number of contacts.
    """
    return (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == user_id)
        .count()
    )


def check_duplicate_contact(
    db: Session,
    user_id: str,
    contact_value: str,
    exclude_contact_id: Optional[str] = None,
) -> bool:
    """
    Check if a contact value already exists for the user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_value: The contact value to check.
        exclude_contact_id: Contact ID to exclude from check (for updates).

    Returns:
        bool: True if duplicate exists, False otherwise.
    """
    query = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == user_id,
        EmergencyContact.contact_value == contact_value,
    )
    if exclude_contact_id:
        query = query.filter(EmergencyContact.id != exclude_contact_id)
    return query.first() is not None


def create_contact(
    db: Session,
    user_id: str,
    data: ContactCreateRequest,
) -> EmergencyContact:
    """
    Create a new emergency contact.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        data: Contact creation data.

    Returns:
        EmergencyContact: The created contact.

    Raises:
        ValueError: If validation fails.
    """
    # Validate contact value based on type
    if data.contact_type == ContactType.EMAIL:
        if not validate_email(data.contact_value):
            raise ValueError("Invalid email format")
    elif data.contact_type == ContactType.SMS:
        if not validate_phone(data.contact_value):
            raise ValueError("Invalid phone number format")

    contact = EmergencyContact(
        user_id=user_id,
        name=data.name,
        contact_type=data.contact_type.value,
        contact_value=data.contact_value,
        priority=data.priority,
        is_verified=False,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(
    db: Session,
    user_id: str,
    contact_id: str,
    data: ContactUpdateRequest,
) -> Optional[EmergencyContact]:
    """
    Update an existing emergency contact.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.
        data: Update data.

    Returns:
        EmergencyContact or None: The updated contact if found, None otherwise.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return None

    if data.name is not None:
        contact.name = data.name
    if data.priority is not None:
        contact.priority = data.priority

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(
    db: Session,
    user_id: str,
    contact_id: str,
) -> bool:
    """
    Delete an emergency contact.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.

    Returns:
        bool: True if deleted, False if not found.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return False

    db.delete(contact)
    db.commit()
    return True


def verify_contact(db: Session, contact_id: str) -> Optional[EmergencyContact]:
    """
    Mark a contact as verified.

    Args:
        db: Database session.
        contact_id: The contact's unique identifier.

    Returns:
        EmergencyContact or None: The verified contact if found, None otherwise.
    """
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
    if contact is None:
        return None

    contact.is_verified = True
    db.commit()
    db.refresh(contact)
    return contact


def send_verification(
    db: Session,
    user_id: str,
    contact_id: str,
) -> tuple[bool, Optional[EmergencyContact]]:
    """
    Send verification to a contact.

    Note: Actual sending logic will be implemented in notifications module.
    This function prepares the verification request.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.

    Returns:
        tuple: (success, contact) - success boolean and contact if found.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return False, None

    # TODO: Integrate with notification service to send actual verification
    # For now, we just return success to indicate the request was valid
    return True, contact


def reorder_priorities(db: Session, user_id: str) -> None:
    """
    Reorder contact priorities to fill gaps.

    This ensures priorities are always consecutive (1, 2, 3).

    Args:
        db: Database session.
        user_id: The user's unique identifier.
    """
    contacts = get_contacts(db, user_id)
    for idx, contact in enumerate(contacts, start=1):
        if contact.priority != idx:
            contact.priority = idx
    db.commit()


# Consent Management Functions


def request_consent(
    db: Session,
    user_id: str,
    contact_id: str,
) -> Optional[EmergencyContact]:
    """
    Generate consent request for a contact.

    Creates a consent token and sets the expiration time.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.

    Returns:
        EmergencyContact or None: The updated contact if found.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return None

    # Generate consent token
    contact.consent_token = secrets.token_urlsafe(48)
    contact.consent_requested_at = datetime.now(timezone.utc)
    contact.consent_expires_at = datetime.now(timezone.utc) + timedelta(
        days=CONSENT_TOKEN_VALIDITY_DAYS
    )
    contact.status = CONSENT_STATUS_PENDING
    contact.consent_responded_at = None

    db.commit()
    db.refresh(contact)
    return contact


def get_contact_by_consent_token(
    db: Session,
    token: str,
) -> Optional[EmergencyContact]:
    """
    Get a contact by consent token.

    Args:
        db: Database session.
        token: The consent token.

    Returns:
        EmergencyContact or None: The contact if found and token is valid.
    """
    now = datetime.now(timezone.utc)
    contact = (
        db.query(EmergencyContact)
        .filter(
            EmergencyContact.consent_token == token,
            EmergencyContact.consent_expires_at > now,
        )
        .first()
    )
    return contact


def process_consent(
    db: Session,
    token: str,
    approved: bool,
) -> Optional[EmergencyContact]:
    """
    Process consent response (approve or reject).

    Args:
        db: Database session.
        token: The consent token.
        approved: Whether the contact approves.

    Returns:
        EmergencyContact or None: The updated contact if found and processed.
    """
    contact = get_contact_by_consent_token(db, token)
    if contact is None:
        return None

    now = datetime.now(timezone.utc)
    contact.status = CONSENT_STATUS_APPROVED if approved else CONSENT_STATUS_REJECTED
    contact.consent_responded_at = now
    contact.consent_token = None  # Invalidate the token after use

    # If approved, also mark as verified
    if approved:
        contact.is_verified = True

    db.commit()
    db.refresh(contact)
    return contact


def get_consent_status(
    db: Session,
    user_id: str,
    contact_id: str,
) -> Optional[dict]:
    """
    Get consent status for a contact.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        contact_id: The contact's unique identifier.

    Returns:
        dict or None: Consent status information if contact found.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return None

    # Check if consent has expired
    if (
        contact.status == CONSENT_STATUS_PENDING
        and contact.consent_expires_at
        and contact.consent_expires_at < datetime.now(timezone.utc)
    ):
        contact.status = CONSENT_STATUS_EXPIRED
        db.commit()
        db.refresh(contact)

    return {
        "contact_id": contact.id,
        "status": contact.status,
        "requested_at": contact.consent_requested_at,
        "responded_at": contact.consent_responded_at,
        "expires_at": contact.consent_expires_at,
    }


def get_active_contacts(db: Session, user_id: str) -> list[EmergencyContact]:
    """
    Get only approved (consented) emergency contacts for a user.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        list[EmergencyContact]: List of approved contacts ordered by priority.
    """
    return (
        db.query(EmergencyContact)
        .filter(
            EmergencyContact.user_id == user_id,
            EmergencyContact.status == CONSENT_STATUS_APPROVED,
            EmergencyContact.is_verified == True,  # noqa: E712
        )
        .order_by(EmergencyContact.priority)
        .all()
    )


def check_expired_consents(db: Session) -> int:
    """
    Check and update expired consent requests.

    Args:
        db: Database session.

    Returns:
        int: Number of consents marked as expired.
    """
    now = datetime.now(timezone.utc)
    updated = (
        db.query(EmergencyContact)
        .filter(
            EmergencyContact.status == CONSENT_STATUS_PENDING,
            EmergencyContact.consent_expires_at < now,
        )
        .update({"status": CONSENT_STATUS_EXPIRED}, synchronize_session=False)
    )
    db.commit()
    return updated
