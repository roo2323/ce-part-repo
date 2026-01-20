"""
NotificationLog model for SoloCheck.

This module defines the NotificationLog SQLAlchemy model for tracking
notification delivery status to emergency contacts.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.contacts.models import EmergencyContact
    from src.users.models import User


class NotificationLog(Base):
    """NotificationLog model for tracking notification delivery."""

    __tablename__ = "notification_logs"

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
    contact_id = Column(
        String(36),
        ForeignKey("emergency_contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(
        String(50),
        nullable=True,
        comment="Notification type: 'status_alert' or 'personal_message'",
    )
    status = Column(
        String(20),
        nullable=True,
        comment="Delivery status: 'pending', 'sent', or 'failed'",
    )
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message = Column(
        String(500),
        nullable=True,
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
        back_populates="notification_logs",
    )
    contact: "EmergencyContact" = relationship(
        "EmergencyContact",
        back_populates="notification_logs",
    )

    def __repr__(self) -> str:
        """Return string representation of NotificationLog."""
        return f"<NotificationLog(id={self.id}, type={self.type}, status={self.status})>"
