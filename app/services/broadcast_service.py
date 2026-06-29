from logging import getLogger

from app.repositories import BroadcastRepositoryProtocol

logger = getLogger(__name__)


class BroadcastService:
    """Manages broadcast messages to users."""

    def __init__(self, broadcast_repo: BroadcastRepositoryProtocol) -> None:
        self._broadcast_repo = broadcast_repo

    async def create_broadcast(
        self,
        broadcast_id: str,
        type_: str,
        content: dict,
        created_by: int,
    ) -> dict:
        doc = {
            "broadcast_id": broadcast_id,
            "type": type_,
            "content": content,
            "status": "pending",
            "total_users": 0,
            "success_count": 0,
            "fail_count": 0,
            "created_by": created_by,
        }
        await self._broadcast_repo.insert_one(doc)
        return doc

    async def update_progress(self, broadcast_id: str, success: int, fail: int) -> None:
        await self._broadcast_repo.update_progress(broadcast_id, success, fail)

    async def get_pending_broadcasts(self) -> list[dict]:
        return await self._broadcast_repo.find_by_status("pending")
