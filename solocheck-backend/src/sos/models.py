"""
SOSEvent model for SoloCheck.

This module defines the SOSEvent SQLAlchemy model for tracking
SOS emergency triggers and their status.
"""
from typing import TYPE_CHECKING
import uuid
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


# SOS status constants
SOS_STATUS_TRIGGERED = "triggered"
SOS_STATUS_CANCELLED = "cancelled"
SOS_STATUS_SENT = "sent"


class SOSEvent(Base):
    """SOSEvent model for tracking emergency SOS triggers."""

    __tablename__ = "sos_events"

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

    # Timing fields
    triggered_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the SOS was triggered",
    )
    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the SOS was cancelled (if cancelled)",
    )
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When notifications were sent",
    )

    # Location fields
    location_lat = Column(
        Numeric(precision=10, scale=8),
        nullable=True,
        comment="Latitude at trigger time",
    )
    location_lng = Column(
        Numeric(precision=11, scale=8),
        nullable=True,
        comment="Longitude at trigger time",
    )

    # Status
    status = Column(
        String(20),
        default=SOS_STATUS_TRIGGERED,
        nullable=False,
        comment="SOS status: 'triggered', 'cancelled', 'sent'",
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
        back_populates="sos_events",
    )

    def __repr__(self) -> str:
        """Return string representation of SOSEvent."""
        return f"<SOSEvent(id={self.id}, user_id={self.user_id}, status={self.status})>"
