"""
Pydantic schemas for Pet endpoints.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.pets.models import PetSpecies


class PetBase(BaseModel):
    """Base schema for pet data."""
    name: str = Field(..., min_length=1, max_length=100)
    species: PetSpecies
    breed: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    weight: Optional[Decimal] = Field(None, ge=0, le=999.99)
    medical_notes: Optional[str] = None
    vet_info: Optional[str] = None
    caretaker_contact: Optional[str] = Field(None, max_length=200)
    photo_url: Optional[str] = Field(None, max_length=500)
    include_in_alert: bool = True


class PetCreate(PetBase):
    """Schema for creating a pet."""
    pass


class PetUpdate(BaseModel):
    """Schema for updating a pet."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[PetSpecies] = None
    breed: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    weight: Optional[Decimal] = Field(None, ge=0, le=999.99)
    medical_notes: Optional[str] = None
    vet_info: Optional[str] = None
    caretaker_contact: Optional[str] = Field(None, max_length=200)
    photo_url: Optional[str] = Field(None, max_length=500)
    include_in_alert: Optional[bool] = None


class PetResponse(BaseModel):
    """Schema for pet response."""
    id: str
    user_id: str
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    weight: Optional[Decimal] = None
    medical_notes: Optional[str] = None
    vet_info: Optional[str] = None
    caretaker_contact: Optional[str] = None
    photo_url: Optional[str] = None
    include_in_alert: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PetListResponse(BaseModel):
    """Schema for pet list response."""
    pets: list[PetResponse]
    total: int


class PetAlertInfo(BaseModel):
    """Schema for pet info included in alerts."""
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[int] = None
    medical_notes: Optional[str] = None
    vet_info: Optional[str] = None
    caretaker_contact: Optional[str] = None
