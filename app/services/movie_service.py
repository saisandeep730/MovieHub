from logging import getLogger

from app.repositories import MovieFileRepositoryProtocol, MovieRepositoryProtocol
from app.utils import generate_movie_id, normalize_title

logger = getLogger(__name__)


class MovieService:
    """Business logic for movie metadata management."""

    def __init__(
        self,
        movie_repo: MovieRepositoryProtocol,
        movie_file_repo: MovieFileRepositoryProtocol,
    ) -> None:
        self._movie_repo = movie_repo
        self._movie_file_repo = movie_file_repo

    async def get_by_movie_id(self, movie_id: str) -> dict | None:
        return await self._movie_repo.find_by_movie_id(movie_id)

    async def get_by_normalized_title(self, title: str) -> dict | None:
        return await self._movie_repo.find_by_normalized_title(normalize_title(title))

    async def movie_exists(self, title: str, year: int) -> bool:
        normalized = normalize_title(title)
        return await self._movie_repo.exists({"normalized_title": normalized, "year": year})

    async def list_latest(self, status: str, skip: int, limit: int) -> list[dict]:
        return await self._movie_repo.find_latest(status, skip, limit)

    async def get_files_for_movie(self, movie_id: str) -> list[dict]:
        return await self._movie_file_repo.find_by_movie_id(movie_id)

    async def count_movies(self, status: str | None = None) -> int:
        filter_: dict = {}
        if status:
            filter_["status"] = status
        return await self._movie_repo.count(filter_)
