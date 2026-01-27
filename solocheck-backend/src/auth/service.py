"""
Authentication service layer.

This module contains the business logic for user authentication,
including registration, login, and token management.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.schemas import RegisterRequest
from src.common.exceptions import (
    DuplicateEmailException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
)
from src.common.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from src.users.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by email address.

    Args:
        db: Database session.
        email: User's email address.

    Returns:
        User if found, None otherwise.
    """
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """
    Retrieve a user by ID.

    Args:
        db: Database session.
        user_id: User's unique identifier.

    Returns:
        User if found, None otherwise.
    """
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def register(db: Session, data: RegisterRequest) -> User:
    """
    Register a new user.

    Args:
        db: Database session.
        data: Registration request data.

    Returns:
        The newly created User.

    Raises:
        DuplicateEmailException: If email is already registered.
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise DuplicateEmailException()

    # Create new user
    hashed_password = get_password_hash(data.password)
    user = User(
        email=data.email,
        password_hash=hashed_password,
        nickname=data.nickname,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.

    Args:
        db: Database session.
        email: User's email address.
        password: User's plain text password.

    Returns:
        User if authentication successful, None otherwise.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_tokens(user: User) -> tuple[str, str]:
    """
    Create access and refresh tokens for a user.

    Args:
        user: The user to create tokens for.

    Returns:
        Tuple of (access_token, refresh_token).
    """
    token_data = {"sub": user.id, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return access_token, refresh_token


def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    """
    Refresh access and refresh tokens using a valid refresh token.

    Args:
        db: Database session.
        refresh_token: The refresh token to validate.

    Returns:
        Tuple of (new_access_token, new_refresh_token).

    Raises:
        InvalidTokenException: If refresh token is invalid or expired.
        UserNotFoundException: If user no longer exists.
    """
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise InvalidTokenException("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException("Invalid token payload")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise UserNotFoundException()

    return create_tokens(user)


def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    """
    Login a user and return tokens.

    Args:
        db: Database session.
        email: User's email address.
        password: User's plain text password.

    Returns:
        Tuple of (user, access_token, refresh_token).

    Raises:
        InvalidCredentialsException: If email or password is incorrect.
    """
    user = authenticate(db, email, password)
    if user is None:
        raise InvalidCredentialsException()

    access_token, refresh_token = create_tokens(user)
    return user, access_token, refresh_token


def send_password_reset_email(email: str) -> None:
    """
    Send a password reset email to the user.

    This is a placeholder implementation. In production, this would
    integrate with SendGrid to send actual emails.

    Args:
        email: User's email address.
    """
    # TODO: Implement actual email sending via SendGrid
    # For now, just log the request
    pass


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """
    Change user's password.

    Args:
        db: Database session.
        user: The user changing their password.
        current_password: Current password for verification.
        new_password: New password to set.

    Raises:
        InvalidCredentialsException: If current password is incorrect.
    """
    if not verify_password(current_password, user.password_hash):
        raise InvalidCredentialsException("현재 비밀번호가 올바르지 않습니다.")

    user.password_hash = get_password_hash(new_password)
    db.commit()
