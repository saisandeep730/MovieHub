from logging import getLogger

from app.repositories import MovieRepositoryProtocol
from app.utils import sanitize_search_query

logger = getLogger(__name__)


class SearchService:
    """Handles movie search with text index and fallback logic."""

    def __init__(self, movie_repo: MovieRepositoryProtocol) -> None:
        self._movie_repo = movie_repo

    async def search(self, query: str, skip: int = 0, limit: int = 20) -> list[dict]:
        cleaned = sanitize_search_query(query)
        if not cleaned:
            return []
        return await self._movie_repo.search(cleaned, skip, limit)

    async def search_by_prefix(self, prefix: str, limit: int = 10) -> list[dict]:
        cleaned = sanitize_search_query(prefix)
        if not cleaned:
            return []
        results = await self._movie_repo.find_many(
            {"normalized_title": {"$regex": f"^{cleaned}"}},
            limit=limit,
            sort=[("created_at", -1)],
        )
        return results

    async def count_results(self, query: str) -> int:
        cleaned = sanitize_search_query(query)
        if not cleaned:
            return 0
        return await self._movie_repo.count({"$text": {"$search": cleaned}})
