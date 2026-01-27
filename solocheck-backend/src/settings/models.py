"""
ReminderSettings model for SoloCheck.

This module defines the ReminderSettings SQLAlchemy model for storing
user's customizable reminder preferences.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class ReminderSettings(Base):
    """ReminderSettings model for storing user's reminder preferences."""

    __tablename__ = "reminder_settings"

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

    # Reminder timing settings
    reminder_hours_before = Column(
        ARRAY(Integer),
        nullable=False,
        default=[48, 24, 12],
        comment="Hours before deadline to send reminders",
    )
    quiet_hours_start = Column(
        Time(),
        nullable=True,
        comment="Start of quiet hours (no notifications)",
    )
    quiet_hours_end = Column(
        Time(),
        nullable=True,
        comment="End of quiet hours",
    )
    preferred_time = Column(
        Time(),
        nullable=True,
        comment="Preferred time for receiving reminders",
    )

    # Channel settings
    push_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable push notification reminders",
    )
    email_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Enable email reminders",
    )

    # Custom message
    custom_message = Column(
        String(100),
        nullable=True,
        comment="Custom reminder message (max 100 chars)",
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
        back_populates="reminder_settings",
    )

    def __repr__(self) -> str:
        """Return string representation of ReminderSettings."""
        return f"<ReminderSettings(id={self.id}, user_id={self.user_id})>"
