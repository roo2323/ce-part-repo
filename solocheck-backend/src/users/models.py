"""
User model for SoloCheck.

This module defines the User SQLAlchemy model with check-in settings,
FCM token for push notifications, and relationships to other models.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.checkin.models import CheckInLog, CheckInSessionToken
    from src.contacts.models import EmergencyContact
    from src.location.models import LocationSharingLog
    from src.messages.models import PersonalMessage
    from src.notifications.models import NotificationLog
    from src.pets.models import Pet
    from src.settings.models import ReminderSettings
    from src.sos.models import SOSEvent
    from src.vault.models import InfoVault


class User(Base):
    """User model representing a SoloCheck user."""

    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash = Column(
        String(255),
        nullable=False,
    )
    nickname = Column(
        String(100),
        nullable=True,
    )

    # Check-in settings
    check_in_cycle = Column(
        Integer,
        default=7,
        nullable=False,
        comment="Check-in cycle in days (7, 14, or 30)",
    )
    grace_period = Column(
        Integer,
        default=48,
        nullable=False,
        comment="Grace period in hours (24, 48, or 72)",
    )
    last_check_in = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Push notification token
    fcm_token = Column(
        String(500),
        nullable=True,
    )

    # Account status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Location consent
    location_consent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user has consented to location sharing",
    )
    location_consent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when location consent was given",
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
    check_in_logs: list["CheckInLog"] = relationship(
        "CheckInLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    emergency_contacts: list["EmergencyContact"] = relationship(
        "EmergencyContact",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    personal_message: "PersonalMessage | None" = relationship(
        "PersonalMessage",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notification_logs: list["NotificationLog"] = relationship(
        "NotificationLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reminder_settings: "ReminderSettings | None" = relationship(
        "ReminderSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    checkin_session_tokens: list["CheckInSessionToken"] = relationship(
        "CheckInSessionToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sos_events: list["SOSEvent"] = relationship(
        "SOSEvent",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    pets: list["Pet"] = relationship(
        "Pet",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    vault_items: list["InfoVault"] = relationship(
        "InfoVault",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    location_sharing_logs: list["LocationSharingLog"] = relationship(
        "LocationSharingLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User(id={self.id}, email={self.email})>"
