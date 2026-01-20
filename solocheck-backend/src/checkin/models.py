"""
CheckInLog model for SoloCheck.

This module defines the CheckInLog SQLAlchemy model for tracking
user check-in history with timestamps and methods.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class CheckInLog(Base):
    """CheckInLog model for recording user check-in activities."""

    __tablename__ = "check_in_logs"

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
    checked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    method = Column(
        String(50),
        nullable=True,
        comment="Check-in method: 'app_open', 'button_click', 'push_response'",
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
        back_populates="check_in_logs",
    )

    def __repr__(self) -> str:
        """Return string representation of CheckInLog."""
        return f"<CheckInLog(id={self.id}, user_id={self.user_id}, method={self.method})>"
