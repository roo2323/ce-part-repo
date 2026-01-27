"""
Pet service for SoloCheck.

Business logic for pet management operations.
"""
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.pets.models import Pet
from src.pets.schemas import PetCreate, PetUpdate, PetAlertInfo


class PetService:
    """Service for pet operations."""

    @staticmethod
    def create_pet(db: Session, user_id: str, data: PetCreate) -> Pet:
        """Create a new pet for a user."""
        pet = Pet(
            user_id=user_id,
            name=data.name,
            species=data.species.value,
            breed=data.breed,
            birth_date=data.birth_date,
            weight=data.weight,
            medical_notes=data.medical_notes,
            vet_info=data.vet_info,
            caretaker_contact=data.caretaker_contact,
            photo_url=data.photo_url,
            include_in_alert=data.include_in_alert,
        )
        db.add(pet)
        db.commit()
        db.refresh(pet)
        return pet

    @staticmethod
    def get_pet(db: Session, user_id: str, pet_id: str) -> Pet:
        """Get a pet by ID for a user."""
        result = db.execute(
            select(Pet).where(Pet.id == pet_id, Pet.user_id == user_id)
        )
        pet = result.scalar_one_or_none()
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found",
            )
        return pet

    @staticmethod
    def get_user_pets(db: Session, user_id: str) -> list[Pet]:
        """Get all pets for a user."""
        result = db.execute(
            select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    def get_pets_for_alert(db: Session, user_id: str) -> list[Pet]:
        """Get pets that should be included in alerts."""
        result = db.execute(
            select(Pet).where(
                Pet.user_id == user_id,
                Pet.include_in_alert == True,
            ).order_by(Pet.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    def update_pet(
        db: Session, user_id: str, pet_id: str, data: PetUpdate
    ) -> Pet:
        """Update a pet."""
        pet = PetService.get_pet(db, user_id, pet_id)

        update_data = data.model_dump(exclude_unset=True)
        if "species" in update_data and update_data["species"] is not None:
            update_data["species"] = update_data["species"].value

        for field, value in update_data.items():
            setattr(pet, field, value)

        db.commit()
        db.refresh(pet)
        return pet

    @staticmethod
    def delete_pet(db: Session, user_id: str, pet_id: str) -> None:
        """Delete a pet."""
        pet = PetService.get_pet(db, user_id, pet_id)
        db.delete(pet)
        db.commit()

    @staticmethod
    def calculate_age_years(birth_date: Optional[date]) -> Optional[int]:
        """Calculate age in years from birth date."""
        if not birth_date:
            return None
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return max(0, age)

    @staticmethod
    def pet_to_alert_info(pet: Pet) -> PetAlertInfo:
        """Convert pet to alert info format."""
        return PetAlertInfo(
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            age_years=PetService.calculate_age_years(pet.birth_date),
            medical_notes=pet.medical_notes,
            vet_info=pet.vet_info,
            caretaker_contact=pet.caretaker_contact,
        )

    @staticmethod
    def get_pets_alert_info(db: Session, user_id: str) -> list[PetAlertInfo]:
        """Get pet alert info for a user."""
        pets = PetService.get_pets_for_alert(db, user_id)
        return [PetService.pet_to_alert_info(pet) for pet in pets]
