from logging import getLogger

from app.repositories import MovieFileRepositoryProtocol, MovieRepositoryProtocol

logger = getLogger(__name__)


class DownloadService:
    """Prepares file download and manages auto-delete lifecycle."""

    def __init__(
        self,
        movie_repo: MovieRepositoryProtocol,
        movie_file_repo: MovieFileRepositoryProtocol,
    ) -> None:
        self._movie_repo = movie_repo
        self._movie_file_repo = movie_file_repo

    async def get_file_for_download(self, file_unique_id: str) -> dict | None:
        return await self._movie_file_repo.find_by_file_unique_id(file_unique_id)

    async def get_movie_with_files(self, movie_id: str) -> dict | None:
        movie = await self._movie_repo.find_by_movie_id(movie_id)
        if not movie:
            return None
        files = await self._movie_file_repo.find_by_movie_id(movie_id)
        movie["files"] = files
        return movie
