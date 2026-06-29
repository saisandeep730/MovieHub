from logging import getLogger

from app.repositories import UserRepositoryProtocol

logger = getLogger(__name__)


class UserService:
    """Manages Telegram user records."""

    def __init__(self, user_repo: UserRepositoryProtocol) -> None:
        self._user_repo = user_repo

    async def register_or_update(self, user_id: int, **fields: str | bool) -> None:
        fields["user_id"] = user_id
        await self._user_repo.upsert_user(fields)

    async def get_user(self, user_id: int) -> dict | None:
        return await self._user_repo.find_by_user_id(user_id)

    async def list_active_users(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return await self._user_repo.find_active(skip, limit)

    async def count_users(self) -> int:
        return await self._user_repo.count()
