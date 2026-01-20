"""
PersonalMessage model for SoloCheck.

This module defines the PersonalMessage SQLAlchemy model for storing
user's personal message to be sent to emergency contacts.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class PersonalMessage(Base):
    """PersonalMessage model for storing user's message to emergency contacts."""

    __tablename__ = "personal_messages"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    content = Column(
        Text,
        nullable=False,
        comment="Encrypted personal message content (max 2000 characters)",
    )
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
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
        back_populates="personal_message",
    )

    def __repr__(self) -> str:
        """Return string representation of PersonalMessage."""
        return f"<PersonalMessage(id={self.id}, user_id={self.user_id}, is_enabled={self.is_enabled})>"
