"""
Info Vault API router for SoloCheck.

Endpoints for vault CRUD operations with encryption.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.users.models import User
from src.vault.schemas import (
    VaultCreate,
    VaultUpdate,
    VaultResponse,
    VaultDetailResponse,
    VaultListResponse,
)
from src.vault.service import VaultService

router = APIRouter()


@router.post(
    "",
    response_model=VaultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a vault item",
    description="Create a new encrypted vault item.",
)
def create_vault_item(
    data: VaultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new vault item."""
    vault_item = VaultService.create_vault_item(db, current_user.id, data)
    return vault_item


@router.get(
    "",
    response_model=VaultListResponse,
    summary="List vault items",
    description="Get all vault items for the current user (without decrypted content).",
)
def list_vault_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all vault items for the current user."""
    items = VaultService.get_user_vault_items(db, current_user.id)
    return VaultListResponse(items=items, total=len(items))


@router.get(
    "/{vault_id}",
    response_model=VaultDetailResponse,
    summary="Get a vault item",
    description="Get a specific vault item with decrypted content.",
)
def get_vault_item(
    vault_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific vault item with decrypted content."""
    vault_item = VaultService.get_vault_item(db, current_user.id, vault_id)
    content = VaultService.decrypt_content(vault_item)
    return VaultDetailResponse(
        id=vault_item.id,
        user_id=vault_item.user_id,
        category=vault_item.category,
        title=vault_item.title,
        content=content,
        include_in_alert=vault_item.include_in_alert,
        created_at=vault_item.created_at,
        updated_at=vault_item.updated_at,
    )


@router.put(
    "/{vault_id}",
    response_model=VaultResponse,
    summary="Update a vault item",
    description="Update a specific vault item.",
)
def update_vault_item(
    vault_id: str,
    data: VaultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a specific vault item."""
    vault_item = VaultService.update_vault_item(
        db, current_user.id, vault_id, data
    )
    return vault_item


@router.delete(
    "/{vault_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vault item",
    description="Delete a specific vault item.",
)
def delete_vault_item(
    vault_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific vault item."""
    VaultService.delete_vault_item(db, current_user.id, vault_id)
    return None
