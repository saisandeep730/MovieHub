from logging import getLogger

from app.repositories import BackupRepositoryProtocol

logger = getLogger(__name__)


class BackupService:
    """Manages system backups and restores."""

    def __init__(self, backup_repo: BackupRepositoryProtocol) -> None:
        self._backup_repo = backup_repo

    async def create_backup(
        self,
        backup_id: str,
        type_: str,
        created_by: int,
    ) -> dict:
        doc = {
            "backup_id": backup_id,
            "type": type_,
            "status": "pending",
            "created_by": created_by,
        }
        await self._backup_repo.insert_one(doc)
        return doc

    async def get_latest_backup(self) -> dict | None:
        return await self._backup_repo.find_latest()

    async def list_backups(self, type_: str | None = None, limit: int = 10) -> list[dict]:
        if type_:
            return await self._backup_repo.find_by_type(type_, limit)
        return await self._backup_repo.find_many({}, limit=limit, sort=[("created_at", -1)])

    async def mark_completed(self, backup_id: str, file_id: str, file_size: int) -> None:
        await self._backup_repo.update_one(
            {"_id": backup_id},
            {"status": "completed", "file_id": file_id, "file_size": file_size},
        )

    async def mark_failed(self, backup_id: str) -> None:
        await self._backup_repo.update_one({"_id": backup_id}, {"status": "failed"})
