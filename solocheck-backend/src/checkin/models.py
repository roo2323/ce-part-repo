"""
CheckInLog and CheckInSessionToken models for SoloCheck.

This module defines the CheckInLog SQLAlchemy model for tracking
user check-in history with timestamps and methods, and CheckInSessionToken
for push notification quick check-in functionality.
"""
from typing import TYPE_CHECKING
import uuid
import secrets

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
        comment="Check-in method: 'app_open', 'button_click', 'push_response', 'widget', 'quick'",
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


class CheckInSessionToken(Base):
    """CheckInSessionToken model for push notification quick check-in."""

    __tablename__ = "checkin_session_tokens"

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
    token = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: secrets.token_urlsafe(48),
        comment="One-time session token for push notification check-in",
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token expiration time (default 1 hour)",
    )
    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when token was used",
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
        back_populates="checkin_session_tokens",
    )

    def __repr__(self) -> str:
        """Return string representation of CheckInSessionToken."""
        return f"<CheckInSessionToken(id={self.id}, user_id={self.user_id})>"
