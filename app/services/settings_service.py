from logging import getLogger
from typing import Any

from app.repositories import SettingsRepositoryProtocol

logger = getLogger(__name__)


class SettingsService:
    """Provides access to all user-facing application settings stored in MongoDB."""

    def __init__(self, settings_repo: SettingsRepositoryProtocol) -> None:
        self._settings_repo = settings_repo

    async def get(self, key: str, default: Any = None) -> Any:
        doc = await self._settings_repo.get(key)
        return doc["value"] if doc else default

    async def set(self, key: str, value: Any, updated_by: int | None = None) -> None:
        await self._settings_repo.set(key, value, updated_by)

    async def get_all(self) -> dict[str, Any]:
        docs = await self._settings_repo.get_all()
        return {doc["key"]: doc["value"] for doc in docs}

    async def get_defaults(self) -> dict[str, Any]:
        return {
            "bot_name": "MovieHub",
            "welcome_message": "Welcome to MovieHub!",
            "about_message": "MovieHub — Your Movie Database",
            "auto_delete_timer": 300,
            "latest_movie_count": 10,
            "force_subscribe_channels": "",
        }
