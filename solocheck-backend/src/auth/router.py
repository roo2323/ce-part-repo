"""
Authentication API router.

This module defines the authentication endpoints for
user registration, login, token refresh, and password reset.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from src.auth.service import (
    change_password,
    create_tokens,
    get_user_by_email,
    login,
    refresh_tokens,
    register,
    send_password_reset_email,
)
from src.auth.dependencies import CurrentActiveUser
from src.database import get_db

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return authentication tokens.",
)
def register_user(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> RegisterResponse:
    """
    Register a new user.

    Args:
        data: Registration data including email, password, and optional nickname.
        db: Database session.

    Returns:
        RegisterResponse with user info and authentication tokens.

    Raises:
        DuplicateEmailException: If email is already registered.
    """
    user = register(db, data)
    access_token, refresh_token = create_tokens(user)

    return RegisterResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password. Supports both JSON body and OAuth2 form data.",
)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """
    Login a user using OAuth2 password flow (form data).

    This endpoint is compatible with OAuth2 and uses form data.
    The 'username' field should contain the email address.

    Args:
        form_data: OAuth2 form data with username (email) and password.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        InvalidCredentialsException: If credentials are incorrect.
    """
    _, access_token, refresh_token = login(db, form_data.username, form_data.password)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login user with JSON",
    description="Authenticate user with email and password using JSON body.",
)
def login_user_json(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """
    Login a user using JSON body.

    This endpoint accepts JSON body with email and password.

    Args:
        data: Login data with email and password.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        InvalidCredentialsException: If credentials are incorrect.
    """
    _, access_token, refresh_token = login(db, data.email, data.password)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
    description="Get new access and refresh tokens using a valid refresh token.",
)
def refresh_user_tokens(
    data: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """
    Refresh authentication tokens.

    Args:
        data: Refresh request with current refresh token.
        db: Database session.

    Returns:
        TokenResponse with new access and refresh tokens.

    Raises:
        InvalidTokenException: If refresh token is invalid or expired.
        UserNotFoundException: If user no longer exists.
    """
    access_token, refresh_token = refresh_tokens(db, data.refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request password reset",
    description="Send a password reset email to the user.",
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ForgotPasswordResponse:
    """
    Request a password reset.

    For security reasons, this endpoint always returns success
    regardless of whether the email exists.

    Args:
        data: Forgot password request with email.
        db: Database session.

    Returns:
        ForgotPasswordResponse with success message.
    """
    # Check if user exists (but don't reveal this to the client)
    user = get_user_by_email(db, data.email)
    if user:
        send_password_reset_email(data.email)

    return ForgotPasswordResponse()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
)
def get_me(
    current_user: CurrentActiveUser,
) -> UserResponse:
    """
    Get current user information.

    Args:
        current_user: The authenticated user.

    Returns:
        UserResponse with user information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        is_active=current_user.is_active,
    )


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="Change password",
    description="Change the authenticated user's password.",
)
def change_user_password(
    data: ChangePasswordRequest,
    current_user: CurrentActiveUser,
    db: Annotated[Session, Depends(get_db)],
) -> ChangePasswordResponse:
    """
    Change user's password.

    Args:
        data: Change password request with current and new password.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        ChangePasswordResponse with success message.

    Raises:
        InvalidCredentialsException: If current password is incorrect.
    """
    change_password(db, current_user, data.current_password, data.new_password)
    return ChangePasswordResponse()
