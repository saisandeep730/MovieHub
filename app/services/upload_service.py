from logging import getLogger

from app.repositories import MovieFileRepositoryProtocol, MovieRepositoryProtocol
from app.utils import generate_movie_id, normalize_title

logger = getLogger(__name__)


class UploadService:
    """Coordinates the multi-step movie upload workflow."""

    def __init__(
        self,
        movie_repo: MovieRepositoryProtocol,
        movie_file_repo: MovieFileRepositoryProtocol,
    ) -> None:
        self._movie_repo = movie_repo
        self._movie_file_repo = movie_file_repo

    async def create_movie_draft(
        self,
        title: str,
        year: int,
        created_by: int,
    ) -> dict:
        movie_id = await generate_movie_id(self._movie_repo)
        movie = {
            "movie_id": movie_id,
            "title": title,
            "normalized_title": normalize_title(title),
            "year": year,
            "status": "draft",
            "created_by": created_by,
            "poster_file_id": None,
        }
        await self._movie_repo.insert_one(movie)
        return movie

    async def set_poster(self, movie_id: str, file_id: str) -> None:
        await self._movie_repo.update_one({"movie_id": movie_id}, {"poster_file_id": file_id})

    async def add_files(self, movie_id: str, files: list[dict]) -> list[str]:
        for f in files:
            f["movie_id"] = movie_id
        return await self._movie_file_repo.insert_many(files)

    async def publish_movie(self, movie_id: str) -> None:
        await self._movie_repo.update_one({"movie_id": movie_id}, {"status": "public"})

    async def duplicate_check(self, title: str, year: int) -> dict | None:
        normalized = normalize_title(title)
        return await self._movie_repo.find_by_normalized_title(normalized)
