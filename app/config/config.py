from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MovieHub application configuration loaded from environment variables."""

    BOT_TOKEN: str = Field(..., min_length=1)
    API_ID: int
    API_HASH: str = Field(..., min_length=1)
    MONGODB_URI: str = Field(..., min_length=1)
    DATABASE_NAME: str = "moviehub"

    ADMIN_IDS: str = ""

    DB_CHANNEL_ID: int
    LOG_CHANNEL_ID: int
    BACKUP_CHANNEL_ID: int

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    @property
    def admin_ids(self) -> set[int]:
        if not self.ADMIN_IDS:
            return set()
        return {int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
