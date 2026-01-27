"""
Pydantic schemas for Info Vault endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.vault.models import VaultCategory


class VaultBase(BaseModel):
    """Base schema for vault data."""
    category: VaultCategory
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, description="Plaintext content to be encrypted")
    include_in_alert: bool = False


class VaultCreate(VaultBase):
    """Schema for creating a vault item."""
    pass


class VaultUpdate(BaseModel):
    """Schema for updating a vault item."""
    category: Optional[VaultCategory] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, description="Plaintext content to be encrypted")
    include_in_alert: Optional[bool] = None


class VaultResponse(BaseModel):
    """Schema for vault item response (without decrypted content)."""
    id: str
    user_id: str
    category: str
    title: str
    include_in_alert: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VaultDetailResponse(VaultResponse):
    """Schema for vault item detail response (with decrypted content)."""
    content: str


class VaultListResponse(BaseModel):
    """Schema for vault list response."""
    items: list[VaultResponse]
    total: int


class VaultAlertInfo(BaseModel):
    """Schema for vault info included in alerts."""
    category: str
    title: str
    content: str
