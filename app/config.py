from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

class Settings(BaseSettings):
    """
    Конфиг из .env / env.

    ВАЖНО:
    - Используем DB_* параметры и формируем SQLAlchemy URL-объект (URL.create),
      чтобы SQLAlchemy передал параметры подключению как kwargs, а не DSN-строкой.
      Это обычно убирает UnicodeDecodeError в psycopg2/libpq на Windows.
    - DATABASE_URL можно оставить как override, но лучше НЕ использовать,
      пока не вылечим проблему окончательно.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    app_name: str = Field(default="library_system", alias="APP_NAME")
    environment: str = Field(default="dev", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # API
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    # Database parts (preferred)
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="library_db", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    db_driver: str = Field(default="psycopg2", alias="DB_DRIVER")  # psycopg2 | psycopg
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Optional override (не рекомендую при проблемах с кодировкой)
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    # Auth
    secret_key: str = Field(default="change_me", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    def sqlalchemy_url_obj(self) -> URL:
        """
        Возвращает SQLAlchemy URL object.
        """
        if self.database_url:
            # Использовать только если уверен, что строка чистая
            return URL.create(self.database_url.strip())

        return URL.create(
            drivername=f"postgresql+{self.db_driver}",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    def cors_origins_list(self) -> list[str]:
        raw = (self.cors_allow_origins or "").strip()
        if raw in ("", "*"):
            return ["*"]
        return [x.strip() for x in raw.split(",") if x.strip()]


settings = Settings()
