# Auth module

from src.auth.dependencies import (
    CurrentActiveUser,
    CurrentUser,
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
)
from src.auth.router import router
from src.auth.schemas import (
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
    authenticate,
    create_tokens,
    get_user_by_email,
    get_user_by_id,
    login,
    refresh_tokens,
    register,
)

__all__ = [
    # Router
    "router",
    # Dependencies
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "CurrentUser",
    "CurrentActiveUser",
    # Schemas
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "UserResponse",
    # Service
    "get_user_by_email",
    "get_user_by_id",
    "register",
    "authenticate",
    "create_tokens",
    "refresh_tokens",
    "login",
]
