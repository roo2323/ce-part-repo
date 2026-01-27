"""
Pets module for SoloCheck.

This module provides pet information management functionality
for users to store information about their pets that can be
included in emergency alerts.
"""

from src.pets.models import Pet, PetSpecies
from src.pets.router import router
from src.pets.service import PetService

__all__ = [
    "Pet",
    "PetSpecies",
    "router",
    "PetService",
]
