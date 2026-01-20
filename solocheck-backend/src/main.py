"""
SoloCheck API - Main FastAPI Application

1인 가구 안부 확인 서비스
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.checkin.router import router as checkin_router
from src.config import settings
from src.contacts.router import router as contacts_router
from src.messages.router import router as messages_router
from src.users.router import router as users_router

# Import all models to ensure SQLAlchemy relationships are properly resolved
from src.users.models import User  # noqa: F401
from src.checkin.models import CheckInLog  # noqa: F401
from src.contacts.models import EmergencyContact  # noqa: F401
from src.messages.models import PersonalMessage  # noqa: F401
from src.notifications.models import NotificationLog  # noqa: F401

# Create FastAPI application
app = FastAPI(
    title="SoloCheck API",
    description="1인 가구 안부 확인 서비스 - 장기 미연락 상황 감지 및 비상연락처 자동 알림",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "1인 가구 안부 확인 서비스",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for container orchestration.

    Returns:
        dict: Health status of the service.
    """
    return {"status": "ok"}


@app.get("/api/v1/health", tags=["Health"])
def api_health_check():
    """
    API v1 health check endpoint.

    Returns:
        dict: Health status with additional information.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


# Router registrations
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(checkin_router, prefix="/api/v1/checkin", tags=["Check-in"])
app.include_router(contacts_router, prefix="/api/v1/contacts", tags=["Contacts"])
app.include_router(messages_router, prefix="/api/v1/message", tags=["Messages"])
