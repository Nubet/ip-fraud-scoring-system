from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    maxmind_db_path: str | None = Field(default=None, alias="MAXMIND_DB_PATH")
    velocity_ttl_seconds: int = Field(default=60, alias="VELOCITY_TTL_SECONDS")
    velocity_max_size: int = Field(default=100_000, alias="VELOCITY_MAX_SIZE")
    velocity_high_threshold: int = Field(default=10, alias="VELOCITY_HIGH_THRESHOLD")
    valid_api_keys: str = Field(default="dev-key", alias="VALID_API_KEYS")


settings = Settings()
