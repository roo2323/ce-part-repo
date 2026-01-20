"""
Emergency Contacts API router for FastAPI.

This module defines the API endpoints for emergency contact operations
including CRUD and verification.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import CurrentActiveUser
from src.common.exceptions import (
    DuplicateContactException,
    MaxContactsExceededException,
    NotFoundException,
    ValidationException,
)
from src.contacts.schemas import (
    ContactCreateRequest,
    ContactListResponse,
    ContactResponse,
    ContactUpdateRequest,
    VerificationResponse,
)
from src.contacts.service import (
    MAX_CONTACTS,
    check_duplicate_contact,
    create_contact,
    delete_contact,
    get_contact_by_id,
    get_contact_count,
    get_contacts,
    reorder_priorities,
    send_verification,
    update_contact,
)
from src.database import get_db


router = APIRouter()


class ContactNotFoundException(NotFoundException):
    """Exception for contact not found."""

    def __init__(self) -> None:
        """Initialize contact not found exception."""
        super().__init__(
            code="CONTACT_NOT_FOUND",
            message="Contact not found",
        )


@router.get(
    "",
    response_model=ContactListResponse,
    summary="Get emergency contacts",
    description="Get all emergency contacts for the current user.",
)
async def list_contacts(
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> ContactListResponse:
    """
    Get all emergency contacts for the current user.

    Returns contacts ordered by priority (1 = highest).

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        ContactListResponse: List of contacts with metadata.
    """
    contacts = get_contacts(db, current_user.id)
    return ContactListResponse(
        data=[ContactResponse.model_validate(c) for c in contacts],
        max_contacts=MAX_CONTACTS,
        current_count=len(contacts),
    )


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create emergency contact",
    description="Create a new emergency contact. Maximum 3 contacts allowed.",
)
async def create_new_contact(
    request: ContactCreateRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> ContactResponse:
    """
    Create a new emergency contact.

    Business rules:
    - Maximum 3 contacts per user
    - No duplicate contact values
    - Contact type must be 'email' or 'sms'
    - Priority range: 1-3

    Args:
        request: Contact creation data.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        ContactResponse: The created contact.

    Raises:
        MaxContactsExceededException: If user already has 3 contacts.
        DuplicateContactException: If contact value already exists.
        ValidationException: If contact value format is invalid.
    """
    # Check maximum contacts limit
    current_count = get_contact_count(db, current_user.id)
    if current_count >= MAX_CONTACTS:
        raise MaxContactsExceededException()

    # Check for duplicate contact value
    if check_duplicate_contact(db, current_user.id, request.contact_value):
        raise DuplicateContactException()

    # Create the contact
    try:
        contact = create_contact(db, current_user.id, request)
    except ValueError as e:
        raise ValidationException(
            code="INVALID_CONTACT_VALUE",
            message=str(e),
        )

    return ContactResponse.model_validate(contact)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Get emergency contact",
    description="Get a specific emergency contact by ID.",
)
async def get_single_contact(
    contact_id: str,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> ContactResponse:
    """
    Get a specific emergency contact.

    Args:
        contact_id: The contact's unique identifier.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        ContactResponse: The contact details.

    Raises:
        ContactNotFoundException: If contact not found.
    """
    contact = get_contact_by_id(db, current_user.id, contact_id)
    if contact is None:
        raise ContactNotFoundException()

    return ContactResponse.model_validate(contact)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Update emergency contact",
    description="Update an existing emergency contact's name or priority.",
)
async def update_existing_contact(
    contact_id: str,
    request: ContactUpdateRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> ContactResponse:
    """
    Update an existing emergency contact.

    Only name and priority can be updated.
    To change contact_type or contact_value, delete and recreate.

    Args:
        contact_id: The contact's unique identifier.
        request: Update data.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        ContactResponse: The updated contact.

    Raises:
        ContactNotFoundException: If contact not found.
    """
    contact = update_contact(db, current_user.id, contact_id, request)
    if contact is None:
        raise ContactNotFoundException()

    return ContactResponse.model_validate(contact)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete emergency contact",
    description="Delete an emergency contact.",
)
async def delete_existing_contact(
    contact_id: str,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete an emergency contact.

    After deletion, priorities may be reordered to fill gaps.

    Args:
        contact_id: The contact's unique identifier.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Raises:
        ContactNotFoundException: If contact not found.
    """
    deleted = delete_contact(db, current_user.id, contact_id)
    if not deleted:
        raise ContactNotFoundException()

    # Reorder priorities to fill gaps
    reorder_priorities(db, current_user.id)


@router.post(
    "/{contact_id}/verify",
    response_model=VerificationResponse,
    summary="Request contact verification",
    description="Send a verification request to the contact.",
)
async def request_verification(
    contact_id: str,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> VerificationResponse:
    """
    Request verification for an emergency contact.

    Sends a verification message to the contact's email or phone.

    Args:
        contact_id: The contact's unique identifier.
        current_user: The authenticated user from JWT token.
        db: Database session.

    Returns:
        VerificationResponse: Verification request status.

    Raises:
        ContactNotFoundException: If contact not found.
    """
    success, contact = send_verification(db, current_user.id, contact_id)
    if not success or contact is None:
        raise ContactNotFoundException()

    return VerificationResponse(
        message="Verification request sent",
        contact_id=contact.id,
        sent_to=contact.contact_value,
    )
