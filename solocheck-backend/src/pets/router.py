"""
Pet API router for SoloCheck.

Endpoints for pet CRUD operations.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.users.models import User
from src.pets.schemas import (
    PetCreate,
    PetUpdate,
    PetResponse,
    PetListResponse,
)
from src.pets.service import PetService

router = APIRouter()


@router.post(
    "",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pet",
    description="Create a new pet for the current user.",
)
def create_pet(
    data: PetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new pet."""
    pet = PetService.create_pet(db, current_user.id, data)
    return pet


@router.get(
    "",
    response_model=PetListResponse,
    summary="List pets",
    description="Get all pets for the current user.",
)
def list_pets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all pets for the current user."""
    pets = PetService.get_user_pets(db, current_user.id)
    return PetListResponse(pets=pets, total=len(pets))


@router.get(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Get a pet",
    description="Get a specific pet by ID.",
)
def get_pet(
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific pet by ID."""
    pet = PetService.get_pet(db, current_user.id, pet_id)
    return pet


@router.put(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Update a pet",
    description="Update a specific pet by ID.",
)
def update_pet(
    pet_id: str,
    data: PetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a specific pet by ID."""
    pet = PetService.update_pet(db, current_user.id, pet_id, data)
    return pet


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pet",
    description="Delete a specific pet by ID.",
)
def delete_pet(
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific pet by ID."""
    PetService.delete_pet(db, current_user.id, pet_id)
    return None
