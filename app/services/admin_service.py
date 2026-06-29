from logging import getLogger

from app.repositories import AdminRepositoryProtocol

logger = getLogger(__name__)


class AdminService:
    """Manages administrator accounts and permissions."""

    def __init__(self, admin_repo: AdminRepositoryProtocol) -> None:
        self._admin_repo = admin_repo

    async def is_admin(self, user_id: int) -> bool:
        return await self._admin_repo.is_admin(user_id)

    async def add_admin(self, user_id: int, username: str, added_by: int, is_superadmin: bool = False) -> dict:
        doc = {
            "user_id": user_id,
            "username": username,
            "added_by": added_by,
            "role": "superadmin" if is_superadmin else "admin",
            "is_active": True,
        }
        await self._admin_repo.insert_one(doc)
        return doc

    async def remove_admin(self, user_id: int) -> None:
        await self._admin_repo.update_one({"user_id": user_id}, {"is_active": False})

    async def list_admins(self) -> list[dict]:
        return await self._admin_repo.find_all_active()

    async def count_admins(self) -> int:
        return await self._admin_repo.count()
