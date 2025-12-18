from typing import Annotated
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: Annotated[str, Field(
        default="postgresql+asyncpg://admin:admin1234@localhost:5432/db",
        description="PostgreSQL connection string"
    )]

    # Application
    APP_NAME: Annotated[str, Field(default="Todo Service", description="Application name")]
    DEBUG: Annotated[bool, Field(default=False, description="Debug mode")]
    LOG_LEVEL: Annotated[str, Field(default="INFO", description="Logging level")]

    # Server
    HOST: Annotated[str, Field(default="0.0.0.0", description="Server host")]
    PORT: Annotated[int, Field(default=8000, ge=1, le=65535, description="Server port")]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Валидация DATABASE_URL."""
        if not v.startswith(("postgresql+asyncpg://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL must start with postgresql+asyncpg:// or postgresql+psycopg://")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Валидация LOG_LEVEL."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
