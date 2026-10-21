from __future__ import annotations

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "dev", "staging", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """Validated application settings loaded from environment and .env."""

    app_name: str = "template-lab"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: LogLevel = "INFO"
    environment: Environment = "local"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("app_name", "host")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        """Trim surrounding whitespace and reject blank text values."""
        value = value.strip()
        if not value:
            raise ValueError("Field must not be blank")
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        """Normalize log levels before validating their allowed values."""
        if not isinstance(value, str):
            return value
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_production_safety(self) -> Self:
        """Reject debug mode in production deployments."""
        if self.environment == "prod" and self.debug:
            raise ValueError("DEBUG=true is forbidden when ENVIRONMENT=prod")
        return self

    @property
    def docs_enabled(self) -> bool:
        """Return whether interactive API documentation should be exposed."""
        return self.environment in {"local", "dev"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
