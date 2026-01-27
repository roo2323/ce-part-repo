"""
Vault service for SoloCheck.

Business logic for info vault operations with encryption.
"""
import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import settings
from src.vault.models import InfoVault
from src.vault.schemas import VaultCreate, VaultUpdate, VaultAlertInfo


class VaultEncryption:
    """Encryption handler for vault content."""

    def __init__(self, key: Optional[str] = None):
        """Initialize with encryption key."""
        encryption_key = key or settings.vault_encryption_key
        if not encryption_key:
            # Generate a key for development (should be set in production)
            encryption_key = Fernet.generate_key().decode()
        elif len(encryption_key) == 32:
            # If it's a raw 32-byte key, encode it as base64
            encryption_key = base64.urlsafe_b64encode(encryption_key.encode()).decode()

        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext content."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt encrypted content."""
        return self.fernet.decrypt(ciphertext.encode()).decode()


class VaultService:
    """Service for vault operations."""

    _encryption: Optional[VaultEncryption] = None

    @classmethod
    def get_encryption(cls) -> VaultEncryption:
        """Get or create encryption instance."""
        if cls._encryption is None:
            cls._encryption = VaultEncryption()
        return cls._encryption

    @staticmethod
    def create_vault_item(
        db: Session, user_id: str, data: VaultCreate
    ) -> InfoVault:
        """Create a new vault item."""
        encryption = VaultService.get_encryption()
        encrypted_content = encryption.encrypt(data.content)

        vault_item = InfoVault(
            user_id=user_id,
            category=data.category.value,
            title=data.title,
            content_encrypted=encrypted_content,
            include_in_alert=data.include_in_alert,
        )
        db.add(vault_item)
        db.commit()
        db.refresh(vault_item)
        return vault_item

    @staticmethod
    def get_vault_item(
        db: Session, user_id: str, vault_id: str
    ) -> InfoVault:
        """Get a vault item by ID."""
        result = db.execute(
            select(InfoVault).where(
                InfoVault.id == vault_id, InfoVault.user_id == user_id
            )
        )
        vault_item = result.scalar_one_or_none()
        if not vault_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vault item not found",
            )
        return vault_item

    @staticmethod
    def get_user_vault_items(
        db: Session, user_id: str
    ) -> list[InfoVault]:
        """Get all vault items for a user."""
        result = db.execute(
            select(InfoVault)
            .where(InfoVault.user_id == user_id)
            .order_by(InfoVault.category, InfoVault.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    def get_vault_items_for_alert(
        db: Session, user_id: str
    ) -> list[InfoVault]:
        """Get vault items that should be included in alerts."""
        result = db.execute(
            select(InfoVault).where(
                InfoVault.user_id == user_id,
                InfoVault.include_in_alert == True,
            ).order_by(InfoVault.category, InfoVault.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    def update_vault_item(
        db: Session, user_id: str, vault_id: str, data: VaultUpdate
    ) -> InfoVault:
        """Update a vault item."""
        vault_item = VaultService.get_vault_item(db, user_id, vault_id)

        update_data = data.model_dump(exclude_unset=True)

        # Handle content encryption
        if "content" in update_data and update_data["content"] is not None:
            encryption = VaultService.get_encryption()
            update_data["content_encrypted"] = encryption.encrypt(update_data.pop("content"))

        # Handle category enum
        if "category" in update_data and update_data["category"] is not None:
            update_data["category"] = update_data["category"].value

        for field, value in update_data.items():
            setattr(vault_item, field, value)

        db.commit()
        db.refresh(vault_item)
        return vault_item

    @staticmethod
    def delete_vault_item(
        db: Session, user_id: str, vault_id: str
    ) -> None:
        """Delete a vault item."""
        vault_item = VaultService.get_vault_item(db, user_id, vault_id)
        db.delete(vault_item)
        db.commit()

    @staticmethod
    def decrypt_content(vault_item: InfoVault) -> str:
        """Decrypt vault item content."""
        encryption = VaultService.get_encryption()
        return encryption.decrypt(vault_item.content_encrypted)

    @staticmethod
    def vault_item_to_alert_info(vault_item: InfoVault) -> VaultAlertInfo:
        """Convert vault item to alert info format."""
        return VaultAlertInfo(
            category=vault_item.category,
            title=vault_item.title,
            content=VaultService.decrypt_content(vault_item),
        )

    @staticmethod
    def get_vault_alert_info(
        db: Session, user_id: str
    ) -> list[VaultAlertInfo]:
        """Get vault alert info for a user."""
        vault_items = VaultService.get_vault_items_for_alert(db, user_id)
        return [VaultService.vault_item_to_alert_info(item) for item in vault_items]
