"""
EmergencyContact model for SoloCheck.

This module defines the EmergencyContact SQLAlchemy model for storing
user's emergency contacts with priority and verification status.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.notifications.models import NotificationLog
    from src.users.models import User


class EmergencyContact(Base):
    """EmergencyContact model for storing user's emergency contacts."""

    __tablename__ = "emergency_contacts"

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
    name = Column(
        String(100),
        nullable=False,
    )
    contact_type = Column(
        String(20),
        nullable=False,
        comment="Contact type: 'email' or 'sms'",
    )
    contact_value = Column(
        String(255),
        nullable=False,
    )
    priority = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Contact priority (1 = highest)",
    )
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="emergency_contacts",
    )
    notification_logs: list["NotificationLog"] = relationship(
        "NotificationLog",
        back_populates="contact",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of EmergencyContact."""
        return f"<EmergencyContact(id={self.id}, name={self.name}, type={self.contact_type})>"
