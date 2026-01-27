"""
Info Vault module for SoloCheck.

This module provides secure information storage functionality
for users to store sensitive information that can be
included in emergency alerts.
"""

from src.vault.models import InfoVault, VaultCategory
from src.vault.router import router
from src.vault.service import VaultService

__all__ = [
    "InfoVault",
    "VaultCategory",
    "router",
    "VaultService",
]
