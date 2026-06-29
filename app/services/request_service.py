from logging import getLogger

from app.repositories import RequestRepositoryProtocol

logger = getLogger(__name__)


class RequestService:
    """Manages movie requests from users."""

    def __init__(self, request_repo: RequestRepositoryProtocol) -> None:
        self._request_repo = request_repo

    async def submit_request(self, movie_name: str, user_id: int, username: str = "") -> dict:
        existing = await self._request_repo.find_by_movie_name(movie_name)
        if existing:
            await self._request_repo.increment_count(existing["_id"])
            return existing
        doc = {
            "movie_name": movie_name,
            "user_id": user_id,
            "username": username,
            "count": 1,
            "fulfilled": False,
        }
        await self._request_repo.insert_one(doc)
        return doc

    async def list_pending(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return await self._request_repo.find_pending(skip, limit)

    async def mark_fulfilled(self, request_id: str, movie_id: str) -> None:
        await self._request_repo.mark_fulfilled(request_id, movie_id)

    async def count_pending(self) -> int:
        return await self._request_repo.count({"fulfilled": False})
