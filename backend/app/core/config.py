"""Application configuration loaded from environment variables.

Secrets are never hard-coded; see .env.example for the full set of keys.
Integrations (LLM, WhatsApp, Google, S3) fall back to mock/disabled mode when
their credentials are absent, so the app runs end-to-end in local dev.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "ID Job-Site Platform API"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/idjobsite"
    )

    # --- Auth / JWT ---
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=30)

    # --- Redis / arq ---
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- S3-compatible storage ---
    s3_endpoint_url: str | None = Field(default=None)
    s3_region: str = Field(default="us-east-1")
    s3_bucket: str = Field(default="id-jobsite")
    s3_access_key: str | None = Field(default=None)
    s3_secret_key: str | None = Field(default=None)
    presigned_url_ttl_seconds: int = Field(default=900)
    max_upload_size_mb: int = Field(default=50)

    # --- LLM (provider-agnostic) ---
    llm_provider: str = Field(default="mock")  # mock | openai | anthropic | bedrock
    llm_api_key: str | None = Field(default=None)
    llm_model: str | None = Field(default=None)

    # --- WhatsApp Business Cloud API ---
    whatsapp_enabled: bool = Field(default=False)
    whatsapp_token: str | None = Field(default=None)
    whatsapp_phone_number_id: str | None = Field(default=None)
    whatsapp_verify_token: str | None = Field(default=None)

    # --- Google Calendar OAuth ---
    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)
    google_redirect_uri: str | None = Field(default=None)

    # --- Push notifications (FCM HTTP v1) ---
    fcm_enabled: bool = Field(default=False)
    # Path to a Firebase service-account JSON, or the JSON contents directly.
    fcm_service_account: str | None = Field(default=None)
    fcm_project_id: str | None = Field(default=None)

    @property
    def storage_mode(self) -> str:
        """Real S3 when credentials are present, otherwise mock."""
        return "s3" if self.s3_access_key and self.s3_secret_key else "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
