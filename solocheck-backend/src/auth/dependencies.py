"""
Authentication dependencies for FastAPI.

This module provides dependency injection functions for
authentication and authorization in API endpoints.
"""
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.auth.service import get_user_by_id
from src.common.exceptions import (
    InactiveUserException,
    InvalidTokenException,
)
from src.common.security import verify_access_token
from src.database import get_db
from src.users.models import User

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Get the current authenticated user from the JWT token.

    Args:
        token: JWT access token from Authorization header.
        db: Database session.

    Returns:
        The authenticated User.

    Raises:
        InvalidTokenException: If token is invalid or expired.
    """
    payload = verify_access_token(token)
    if payload is None:
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException("Invalid token payload")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise InvalidTokenException("User not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current authenticated user, ensuring they are active.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        The authenticated active User.

    Raises:
        InactiveUserException: If user account is inactive.
    """
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
