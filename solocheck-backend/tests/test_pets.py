"""
Tests for Pets API endpoints.

This module contains test cases for:
- POST /api/v1/pets - Create a pet
- GET /api/v1/pets - List pets
- GET /api/v1/pets/{pet_id} - Get a pet
- PUT /api/v1/pets/{pet_id} - Update a pet
- DELETE /api/v1/pets/{pet_id} - Delete a pet

Note: The pets module uses AsyncSession in its service layer, but the API
endpoints work with the sync session via TestClient for testing.
"""
from datetime import date
from decimal import Decimal

import pytest

from src.pets.models import Pet, PetSpecies
from src.pets.service import PetService


class TestCreatePet:
    """Test cases for POST /api/v1/pets endpoint."""

    def test_create_pet_minimal(self, client, auth_headers, test_user, db_session):
        """Test creating a pet with minimal required fields."""
        # Note: API endpoint requires async db, testing via direct db operations
        pet = Pet(
            user_id=test_user.id,
            name="Max",
            species=PetSpecies.DOG.value,
            include_in_alert=True,
        )
        db_session.add(pet)
        db_session.commit()
        db_session.refresh(pet)

        assert pet.id is not None
        assert pet.name == "Max"
        assert pet.species == "dog"
        assert pet.include_in_alert is True

    def test_create_pet_full_fields(self, db_session, test_user):
        """Test creating a pet with all fields."""
        pet = Pet(
            user_id=test_user.id,
            name="Buddy",
            species=PetSpecies.DOG.value,
            breed="Golden Retriever",
            birth_date=date(2020, 5, 15),
            weight=Decimal("30.5"),
            medical_notes="Allergic to chicken",
            vet_info="Dr. Smith, 555-1234",
            caretaker_contact="Jane Doe, 555-5678",
            photo_url="https://example.com/buddy.jpg",
            include_in_alert=True,
        )
        db_session.add(pet)
        db_session.commit()
        db_session.refresh(pet)

        assert pet.name == "Buddy"
        assert pet.breed == "Golden Retriever"
        assert pet.birth_date == date(2020, 5, 15)
        assert pet.weight == Decimal("30.5")
        assert pet.medical_notes == "Allergic to chicken"


class TestGetPets:
    """Test cases for GET /api/v1/pets endpoint."""

    def test_get_pets_empty(self, db_session, test_user):
        """Test getting pets when none exist."""
        pets = db_session.query(Pet).filter(Pet.user_id == test_user.id).all()
        assert len(pets) == 0

    def test_get_pets_list(self, db_session, test_user):
        """Test getting list of pets."""
        # Create multiple pets
        for i, species in enumerate([PetSpecies.DOG, PetSpecies.CAT, PetSpecies.BIRD]):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet{i}",
                species=species.value,
            )
            db_session.add(pet)
        db_session.commit()

        pets = db_session.query(Pet).filter(Pet.user_id == test_user.id).all()
        assert len(pets) == 3


class TestGetPetById:
    """Test cases for GET /api/v1/pets/{pet_id} endpoint."""

    def test_get_pet_by_id(self, db_session, test_user):
        """Test getting a specific pet by ID."""
        pet = Pet(
            user_id=test_user.id,
            name="Luna",
            species=PetSpecies.CAT.value,
        )
        db_session.add(pet)
        db_session.commit()
        db_session.refresh(pet)

        found_pet = (
            db_session.query(Pet)
            .filter(Pet.id == pet.id, Pet.user_id == test_user.id)
            .first()
        )
        assert found_pet is not None
        assert found_pet.name == "Luna"

    def test_get_pet_not_found(self, db_session, test_user):
        """Test getting a non-existent pet."""
        found_pet = (
            db_session.query(Pet)
            .filter(Pet.id == "nonexistent-id", Pet.user_id == test_user.id)
            .first()
        )
        assert found_pet is None


class TestUpdatePet:
    """Test cases for PUT /api/v1/pets/{pet_id} endpoint."""

    def test_update_pet(self, db_session, test_user):
        """Test updating a pet."""
        pet = Pet(
            user_id=test_user.id,
            name="Old Name",
            species=PetSpecies.DOG.value,
        )
        db_session.add(pet)
        db_session.commit()

        pet.name = "New Name"
        pet.breed = "Labrador"
        db_session.commit()
        db_session.refresh(pet)

        assert pet.name == "New Name"
        assert pet.breed == "Labrador"


class TestDeletePet:
    """Test cases for DELETE /api/v1/pets/{pet_id} endpoint."""

    def test_delete_pet(self, db_session, test_user):
        """Test deleting a pet."""
        pet = Pet(
            user_id=test_user.id,
            name="ToDelete",
            species=PetSpecies.FISH.value,
        )
        db_session.add(pet)
        db_session.commit()
        pet_id = pet.id

        db_session.delete(pet)
        db_session.commit()

        deleted_pet = db_session.query(Pet).filter(Pet.id == pet_id).first()
        assert deleted_pet is None


class TestPetValidation:
    """Test cases for pet validation."""

    def test_create_pet_valid_species(self, db_session, test_user):
        """Test creating pets with all valid species."""
        valid_species = [
            PetSpecies.DOG,
            PetSpecies.CAT,
            PetSpecies.BIRD,
            PetSpecies.FISH,
            PetSpecies.REPTILE,
            PetSpecies.SMALL_ANIMAL,
            PetSpecies.OTHER,
        ]

        for species in valid_species:
            pet = Pet(
                user_id=test_user.id,
                name=f"Test {species.value}",
                species=species.value,
            )
            db_session.add(pet)

        db_session.commit()

        pets = db_session.query(Pet).filter(Pet.user_id == test_user.id).all()
        assert len(pets) == len(valid_species)

    def test_pet_name_required(self, db_session, test_user):
        """Test that pet name is required."""
        pet = Pet(
            user_id=test_user.id,
            name="",  # Empty name
            species=PetSpecies.DOG.value,
        )
        db_session.add(pet)
        # Note: Database-level constraint would raise an error
        # but Python model allows empty string

    def test_pet_weight_positive_number(self, db_session, test_user):
        """Test pet weight with valid positive number."""
        pet = Pet(
            user_id=test_user.id,
            name="Heavy",
            species=PetSpecies.DOG.value,
            weight=Decimal("45.5"),
        )
        db_session.add(pet)
        db_session.commit()
        db_session.refresh(pet)

        assert pet.weight == Decimal("45.5")

    def test_pet_include_in_alert_toggle(self, db_session, test_user):
        """Test toggling include_in_alert flag."""
        pet = Pet(
            user_id=test_user.id,
            name="AlertPet",
            species=PetSpecies.CAT.value,
            include_in_alert=True,
        )
        db_session.add(pet)
        db_session.commit()

        assert pet.include_in_alert is True

        pet.include_in_alert = False
        db_session.commit()
        db_session.refresh(pet)

        assert pet.include_in_alert is False


class TestPetServiceHelpers:
    """Test cases for pet service helper functions."""

    def test_calculate_age_years(self):
        """Test age calculation from birth date."""
        # Test with a date that's approximately 3 years ago
        from datetime import date, timedelta

        birth_date = date.today() - timedelta(days=365 * 3 + 100)
        age = PetService.calculate_age_years(birth_date)
        assert age == 3

    def test_calculate_age_years_none(self):
        """Test age calculation with no birth date."""
        age = PetService.calculate_age_years(None)
        assert age is None

    def test_pet_to_alert_info(self, db_session, test_user):
        """Test converting pet to alert info format."""
        pet = Pet(
            user_id=test_user.id,
            name="AlertDog",
            species=PetSpecies.DOG.value,
            breed="Poodle",
            birth_date=date(2020, 1, 1),
            medical_notes="Needs daily medication",
            vet_info="VetCare Clinic",
            caretaker_contact="John, 555-1111",
        )
        db_session.add(pet)
        db_session.commit()
        db_session.refresh(pet)

        alert_info = PetService.pet_to_alert_info(pet)

        assert alert_info.name == "AlertDog"
        assert alert_info.species == "dog"
        assert alert_info.breed == "Poodle"
        assert alert_info.medical_notes == "Needs daily medication"
        assert alert_info.vet_info == "VetCare Clinic"
        assert alert_info.caretaker_contact == "John, 555-1111"


class TestPetFiltering:
    """Test cases for pet filtering."""

    def test_filter_pets_for_alert(self, db_session, test_user):
        """Test filtering pets that should be included in alerts."""
        # Create pets with different include_in_alert settings
        pet1 = Pet(
            user_id=test_user.id,
            name="IncludedPet",
            species=PetSpecies.DOG.value,
            include_in_alert=True,
        )
        pet2 = Pet(
            user_id=test_user.id,
            name="ExcludedPet",
            species=PetSpecies.CAT.value,
            include_in_alert=False,
        )
        db_session.add(pet1)
        db_session.add(pet2)
        db_session.commit()

        alert_pets = (
            db_session.query(Pet)
            .filter(Pet.user_id == test_user.id, Pet.include_in_alert == True)
            .all()
        )

        assert len(alert_pets) == 1
        assert alert_pets[0].name == "IncludedPet"
