"""
Tests for Info Vault API endpoints.

This module contains test cases for:
- POST /api/v1/vault - Create a vault item
- GET /api/v1/vault - List vault items
- GET /api/v1/vault/{vault_id} - Get a vault item (with decrypted content)
- PUT /api/v1/vault/{vault_id} - Update a vault item
- DELETE /api/v1/vault/{vault_id} - Delete a vault item

Note: Tests focus on business logic since the module uses AsyncSession.
"""
import pytest
from cryptography.fernet import Fernet

from src.vault.models import InfoVault, VaultCategory
from src.vault.service import VaultEncryption, VaultService


class TestVaultEncryption:
    """Test cases for vault encryption functionality."""

    def test_encryption_round_trip(self):
        """Test that content can be encrypted and decrypted."""
        # Generate a test key
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        plaintext = "This is my secret information"
        ciphertext = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(ciphertext)

        assert ciphertext != plaintext
        assert decrypted == plaintext

    def test_content_encrypted_in_db(self, db_session, test_user):
        """Test that content is stored encrypted in database."""
        # Use encryption service
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        plaintext = "My bank account: 1234-5678"
        encrypted_content = encryption.encrypt(plaintext)

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.FINANCIAL.value,
            title="Bank Info",
            content_encrypted=encrypted_content,
            include_in_alert=True,
        )
        db_session.add(vault_item)
        db_session.commit()
        db_session.refresh(vault_item)

        # Verify content is encrypted in DB
        assert vault_item.content_encrypted != plaintext
        assert vault_item.content_encrypted == encrypted_content

    def test_content_decrypted_on_read(self):
        """Test that content is properly decrypted when read."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        original = "Secret medical info: allergic to penicillin"
        encrypted = encryption.encrypt(original)
        decrypted = encryption.decrypt(encrypted)

        assert decrypted == original


class TestCreateVaultItem:
    """Test cases for creating vault items."""

    def test_create_vault_item(self, db_session, test_user):
        """Test creating a vault item."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.MEDICAL.value,
            title="Medical Records",
            content_encrypted=encryption.encrypt("Blood type: O+"),
            include_in_alert=True,
        )
        db_session.add(vault_item)
        db_session.commit()
        db_session.refresh(vault_item)

        assert vault_item.id is not None
        assert vault_item.title == "Medical Records"
        assert vault_item.category == "medical"
        assert vault_item.include_in_alert is True


class TestGetVaultItems:
    """Test cases for retrieving vault items."""

    def test_get_vault_items_empty(self, db_session, test_user):
        """Test getting vault items when none exist."""
        items = (
            db_session.query(InfoVault)
            .filter(InfoVault.user_id == test_user.id)
            .all()
        )
        assert len(items) == 0

    def test_get_vault_items_list(self, db_session, test_user):
        """Test getting list of vault items."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        categories = [
            VaultCategory.MEDICAL,
            VaultCategory.FINANCIAL,
            VaultCategory.HOUSING,
        ]

        for i, category in enumerate(categories):
            vault_item = InfoVault(
                user_id=test_user.id,
                category=category.value,
                title=f"Item {i}",
                content_encrypted=encryption.encrypt(f"Content {i}"),
            )
            db_session.add(vault_item)
        db_session.commit()

        items = (
            db_session.query(InfoVault)
            .filter(InfoVault.user_id == test_user.id)
            .all()
        )
        assert len(items) == 3

    def test_get_vault_item_by_id(self, db_session, test_user):
        """Test getting a specific vault item."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.INSURANCE.value,
            title="Insurance Policy",
            content_encrypted=encryption.encrypt("Policy #12345"),
        )
        db_session.add(vault_item)
        db_session.commit()
        db_session.refresh(vault_item)

        found = (
            db_session.query(InfoVault)
            .filter(
                InfoVault.id == vault_item.id,
                InfoVault.user_id == test_user.id,
            )
            .first()
        )

        assert found is not None
        assert found.title == "Insurance Policy"


class TestUpdateVaultItem:
    """Test cases for updating vault items."""

    def test_update_vault_item(self, db_session, test_user):
        """Test updating a vault item."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.OTHER.value,
            title="Old Title",
            content_encrypted=encryption.encrypt("Old content"),
        )
        db_session.add(vault_item)
        db_session.commit()

        vault_item.title = "New Title"
        vault_item.content_encrypted = encryption.encrypt("New content")
        db_session.commit()
        db_session.refresh(vault_item)

        assert vault_item.title == "New Title"
        assert encryption.decrypt(vault_item.content_encrypted) == "New content"


class TestDeleteVaultItem:
    """Test cases for deleting vault items."""

    def test_delete_vault_item(self, db_session, test_user):
        """Test deleting a vault item."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.MEDICAL.value,
            title="To Delete",
            content_encrypted=encryption.encrypt("Delete me"),
        )
        db_session.add(vault_item)
        db_session.commit()
        vault_id = vault_item.id

        db_session.delete(vault_item)
        db_session.commit()

        deleted = db_session.query(InfoVault).filter(InfoVault.id == vault_id).first()
        assert deleted is None

    def test_vault_item_not_found(self, db_session, test_user):
        """Test getting non-existent vault item."""
        found = (
            db_session.query(InfoVault)
            .filter(
                InfoVault.id == "nonexistent-id",
                InfoVault.user_id == test_user.id,
            )
            .first()
        )
        assert found is None


class TestVaultCategories:
    """Test cases for vault categories."""

    def test_valid_categories(self, db_session, test_user):
        """Test creating vault items with all valid categories."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        valid_categories = [
            VaultCategory.MEDICAL,
            VaultCategory.HOUSING,
            VaultCategory.INSURANCE,
            VaultCategory.FINANCIAL,
            VaultCategory.OTHER,
        ]

        for category in valid_categories:
            vault_item = InfoVault(
                user_id=test_user.id,
                category=category.value,
                title=f"Category {category.value}",
                content_encrypted=encryption.encrypt(f"Content for {category.value}"),
            )
            db_session.add(vault_item)
        db_session.commit()

        items = (
            db_session.query(InfoVault)
            .filter(InfoVault.user_id == test_user.id)
            .all()
        )
        assert len(items) == len(valid_categories)

    def test_filter_by_category(self, db_session, test_user):
        """Test filtering vault items by category."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        # Create items in different categories
        for category in [VaultCategory.MEDICAL, VaultCategory.MEDICAL, VaultCategory.FINANCIAL]:
            vault_item = InfoVault(
                user_id=test_user.id,
                category=category.value,
                title=f"Item in {category.value}",
                content_encrypted=encryption.encrypt("content"),
            )
            db_session.add(vault_item)
        db_session.commit()

        medical_items = (
            db_session.query(InfoVault)
            .filter(
                InfoVault.user_id == test_user.id,
                InfoVault.category == VaultCategory.MEDICAL.value,
            )
            .all()
        )
        assert len(medical_items) == 2


class TestVaultAlertFlag:
    """Test cases for include_in_alert flag."""

    def test_include_in_alert_flag(self, db_session, test_user):
        """Test include_in_alert flag filtering."""
        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)

        # Create items with different alert settings
        vault_included = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.MEDICAL.value,
            title="Included",
            content_encrypted=encryption.encrypt("Include this"),
            include_in_alert=True,
        )
        vault_excluded = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.FINANCIAL.value,
            title="Excluded",
            content_encrypted=encryption.encrypt("Exclude this"),
            include_in_alert=False,
        )
        db_session.add(vault_included)
        db_session.add(vault_excluded)
        db_session.commit()

        alert_items = (
            db_session.query(InfoVault)
            .filter(
                InfoVault.user_id == test_user.id,
                InfoVault.include_in_alert == True,
            )
            .all()
        )

        assert len(alert_items) == 1
        assert alert_items[0].title == "Included"


class TestVaultServiceHelpers:
    """Test cases for vault service helper functions."""

    def test_vault_item_to_alert_info(self, db_session, test_user):
        """Test converting vault item to alert info format."""
        # Reset the encryption instance for test isolation
        VaultService._encryption = None

        key = Fernet.generate_key().decode()
        encryption = VaultEncryption(key)
        VaultService._encryption = encryption

        vault_item = InfoVault(
            user_id=test_user.id,
            category=VaultCategory.MEDICAL.value,
            title="Emergency Medical Info",
            content_encrypted=encryption.encrypt("Blood type: AB-"),
            include_in_alert=True,
        )
        db_session.add(vault_item)
        db_session.commit()
        db_session.refresh(vault_item)

        alert_info = VaultService.vault_item_to_alert_info(vault_item)

        assert alert_info.category == "medical"
        assert alert_info.title == "Emergency Medical Info"
        assert alert_info.content == "Blood type: AB-"

        # Clean up
        VaultService._encryption = None
