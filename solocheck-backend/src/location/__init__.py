"""
Location module for SoloCheck.

This module provides location consent management and
location sharing logging functionality.
"""

from src.location.models import LocationSharingLog
from src.location.router import router
from src.location.service import LocationService

__all__ = [
    "LocationSharingLog",
    "router",
    "LocationService",
]
