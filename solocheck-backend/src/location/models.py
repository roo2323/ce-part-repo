"""
Location Sharing Log model for SoloCheck.

This module defines the LocationSharingLog SQLAlchemy model for tracking
when and with whom location information was shared (legal requirement).
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class LocationSharingLog(Base):
    """LocationSharingLog model for tracking location sharing events."""

    __tablename__ = "location_sharing_logs"

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
    event_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Event type: 'sos' or 'missed_checkin'",
    )
    location_lat = Column(
        Numeric(10, 8),
        nullable=True,
    )
    location_lng = Column(
        Numeric(11, 8),
        nullable=True,
    )
    recipient_ids = Column(
        ARRAY(String(36)),
        nullable=True,
        comment="IDs of contacts who received the location",
    )
    shared_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="location_sharing_logs",
    )

    def __repr__(self) -> str:
        """Return string representation of LocationSharingLog."""
        return f"<LocationSharingLog(id={self.id}, event_type={self.event_type})>"
