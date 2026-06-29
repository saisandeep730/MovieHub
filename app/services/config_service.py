from logging import getLogger
from typing import Any

from app.repositories import SettingsRepositoryProtocol

logger = getLogger(__name__)


class ConfigService:
    """Manages runtime configuration stored in MongoDB (not .env secrets)."""

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

    async def get_bot_name(self) -> str:
        return await self.get("bot_name", "MovieHub")

    async def get_welcome_message(self) -> str:
        return await self.get("welcome_message", "Welcome to MovieHub!")

    async def get_auto_delete_timer(self) -> int:
        return int(await self.get("auto_delete_timer", 300))
