from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    App configuration loaded from environment / .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    app_name: str = Field(default="library_system")
    environment: str = Field(default="dev")  # dev|prod
    debug: bool = Field(default=True)

    # API
    api_prefix: str = Field(default="/api")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:password@localhost:5432/library_db",
        description="SQLAlchemy database URL",
    )
    db_echo: bool = Field(default=False)

    # Auth (for future JWT)
    secret_key: str = Field(default="change_me")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)

    # CORS
    cors_allow_origins: str = Field(default="*")  # comma-separated or "*"
    cors_allow_credentials: bool = Field(default=True)

    def cors_origins_list(self) -> list[str]:
        """
        Returns a list of allowed origins. Supports "*" or comma-separated string.
        """
        raw = (self.cors_allow_origins or "").strip()
        if raw == "*" or raw == "":
            return ["*"]
        return [x.strip() for x in raw.split(",") if x.strip()]


settings = Settings()
