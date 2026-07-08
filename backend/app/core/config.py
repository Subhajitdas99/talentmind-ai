from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # Core application metadata.
    app_name: str = Field(default="TalentMind AI", validation_alias="APP_NAME")
    version: str = Field(default="1.0.0", validation_alias="VERSION")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # Runtime and API behavior.
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    docs_url: str | None = Field(default="/docs", validation_alias="DOCS_URL")
    openapi_url: str | None = Field(default="/openapi.json", validation_alias="OPENAPI_URL")
    redoc_url: str | None = Field(default="/redoc", validation_alias="REDOC_URL")
    allowed_hosts: list[str] = Field(default_factory=lambda: ["*"], validation_alias="ALLOWED_HOSTS")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias="CORS_ORIGINS",
    )

    # Infrastructure connection and security settings.
    database_url: str = Field(
        default="postgresql+psycopg://talentmind:talentmind@localhost:5432/talentmind",
        validation_alias="DATABASE_URL",
    )
    secret_key: str = Field(default="change-me", validation_alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    token_expire_minutes: int = Field(default=60 * 24, validation_alias="TOKEN_EXPIRE_MINUTES")

    # Observability and integrations.
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: str | None = Field(default=None, validation_alias="LOG_FILE")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    @field_validator("environment", mode="before")
    @classmethod
    def _normalize_environment(cls, value: object) -> str | object:
        """Normalize the runtime environment to a lowercase, supported value."""

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"development", "testing", "production"}:
                return normalized
        return value

    @model_validator(mode="after")
    def _validate_runtime_settings(self) -> "Settings":
        if self.environment == "production" and (
            not self.secret_key or self.secret_key == "change-me" or len(self.secret_key) < 32
        ):
            raise ValueError("SECRET_KEY must be set to a strong non-default value in production")
        return self

    @field_validator("allowed_hosts", "cors_origins", mode="before")
    @classmethod
    def _parse_csv(cls, value: object) -> list[str] | object:
        """Allow comma-separated lists for environment-based host overrides."""

        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_bool(cls, value: object) -> bool | object:
        """Accept common string representations of booleans from .env files."""

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        return value

    @property
    def app_version(self) -> str:
        """Backward-compatible alias for the application version."""

        return self.version

    @property
    def jwt_secret_key(self) -> str:
        """Backward-compatible alias for the JWT signing secret."""

        return self.secret_key

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        """Backward-compatible alias for token lifetime."""

        return self.token_expire_minutes

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton settings instance for the process lifetime."""

    return Settings()


# Module-level singleton so every layer reuses the same validated configuration.
settings = get_settings()
