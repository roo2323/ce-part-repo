"""
Pet model for SoloCheck.

This module defines the Pet SQLAlchemy model for storing
user's pet information that can be included in emergency alerts.
"""
from typing import TYPE_CHECKING
import uuid
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class PetSpecies(str, Enum):
    """Pet species enumeration."""
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    SMALL_ANIMAL = "small_animal"  # hamster, rabbit, etc.
    OTHER = "other"


class Pet(Base):
    """Pet model for storing user's pet information."""

    __tablename__ = "pets"

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
    species = Column(
        String(50),
        nullable=False,
        comment="Pet species: dog, cat, bird, fish, reptile, small_animal, other",
    )
    breed = Column(
        String(100),
        nullable=True,
    )
    birth_date = Column(
        Date,
        nullable=True,
    )
    weight = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Weight in kg",
    )
    medical_notes = Column(
        Text,
        nullable=True,
        comment="Health notes, allergies, special care instructions",
    )
    vet_info = Column(
        Text,
        nullable=True,
        comment="Veterinarian/clinic information",
    )
    caretaker_contact = Column(
        String(200),
        nullable=True,
        comment="Emergency caretaker contact info",
    )
    photo_url = Column(
        String(500),
        nullable=True,
    )
    include_in_alert = Column(
        Boolean,
        default=True,
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
        back_populates="pets",
    )

    def __repr__(self) -> str:
        """Return string representation of Pet."""
        return f"<Pet(id={self.id}, name={self.name}, species={self.species})>"
