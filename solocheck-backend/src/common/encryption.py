"""
Encryption utilities for SoloCheck.

This module provides encryption and decryption functions for sensitive data
like personal messages using Fernet symmetric encryption.
"""
import base64
import hashlib

from cryptography.fernet import Fernet

from src.config import settings


def get_encryption_key() -> bytes:
    """
    Get or derive the encryption key from settings.

    If MESSAGE_ENCRYPTION_KEY is not set, derives a key from SECRET_KEY.
    The key must be a valid Fernet key (32 url-safe base64-encoded bytes).

    Returns:
        bytes: A valid Fernet key.
    """
    key = settings.message_encryption_key

    if not key:
        # Derive a key from SECRET_KEY if MESSAGE_ENCRYPTION_KEY is not set
        # This is for development convenience; production should use a dedicated key
        hash_bytes = hashlib.sha256(settings.secret_key.encode()).digest()
        return base64.urlsafe_b64encode(hash_bytes)

    # If the key is provided but not in valid Fernet format, derive one
    try:
        # Check if it's a valid Fernet key
        Fernet(key.encode())
        return key.encode()
    except Exception:
        # Derive a proper key from the provided string
        hash_bytes = hashlib.sha256(key.encode()).digest()
        return base64.urlsafe_b64encode(hash_bytes)


def encrypt_message(content: str) -> str:
    """
    Encrypt a message using Fernet (AES) encryption.

    Args:
        content: The plaintext message to encrypt.

    Returns:
        str: The encrypted message as a base64-encoded string.
    """
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = fernet.encrypt(content.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_message(encrypted: str) -> str:
    """
    Decrypt an encrypted message using Fernet (AES) decryption.

    Args:
        encrypted: The encrypted message as a base64-encoded string.

    Returns:
        str: The decrypted plaintext message.

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails.
    """
    key = get_encryption_key()
    fernet = Fernet(key)
    decrypted_bytes = fernet.decrypt(encrypted.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")
