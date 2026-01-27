"""
Info Vault model for SoloCheck.

This module defines the InfoVault SQLAlchemy model for storing
user's sensitive information with AES-256 encryption.
"""
from typing import TYPE_CHECKING
import uuid
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class VaultCategory(str, Enum):
    """Vault item category enumeration."""
    MEDICAL = "medical"
    HOUSING = "housing"
    INSURANCE = "insurance"
    FINANCIAL = "financial"
    OTHER = "other"


class InfoVault(Base):
    """InfoVault model for storing user's sensitive information."""

    __tablename__ = "info_vault"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Category: medical, housing, insurance, financial, other",
    )
    title = Column(
        String(200),
        nullable=False,
    )
    content_encrypted = Column(
        Text,
        nullable=False,
        comment="AES-256 encrypted content",
    )
    include_in_alert = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether to include in missed check-in alerts",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="vault_items",
    )

    def __repr__(self) -> str:
        """Return string representation of InfoVault."""
        return f"<InfoVault(id={self.id}, title={self.title}, category={self.category})>"
