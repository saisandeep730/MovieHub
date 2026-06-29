from logging import getLogger

from app.database import db_manager
from app.repositories import HealthRepositoryProtocol

logger = getLogger(__name__)


class HealthService:
    """Monitors and reports system component health."""

    def __init__(self, health_repo: HealthRepositoryProtocol) -> None:
        self._health_repo = health_repo

    async def check_database(self) -> dict:
        ok = await db_manager.health_check()
        return {"component": "mongodb", "status": "healthy" if ok else "down"}

    async def log_check(self, component: str, status: str, message: str = "") -> None:
        doc = {
            "component": component,
            "status": status,
            "message": message,
        }
        await self._health_repo.insert_one(doc)

    async def get_latest_checks(self, component: str, limit: int = 10) -> list[dict]:
        return await self._health_repo.find_latest_checks(component, limit)

    async def get_all_status(self) -> dict[str, str]:
        db_status = await self.check_database()
        return {
            "mongodb": db_status["status"],
            "bot": "unknown",
            "telegram": "unknown",
            "database_channel": "unknown",
            "redirect_server": "unknown",
        }
