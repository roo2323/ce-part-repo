"""
Application configuration using Pydantic Settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "하루안부"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://solocheck:solocheck@localhost:5432/solocheck"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Firebase Cloud Messaging
    fcm_credentials_path: Optional[str] = None

    # SendGrid Email
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: str = "noreply@dailyhello.app"

    # Message Encryption
    message_encryption_key: str = ""

    # Vault Encryption Key (Fernet key, 32 bytes base64 encoded)
    vault_encryption_key: str = ""

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
