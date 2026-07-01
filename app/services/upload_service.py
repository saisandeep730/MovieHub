from __future__ import annotations

from datetime import datetime, timezone
from logging import getLogger

from app.repositories import MovieFileRepositoryProtocol, MovieRepositoryProtocol
from app.utils import generate_movie_id, normalize_title
from app.utils.filename_types import ParsedFile

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

    async def create_movie_document(
        self,
        title: str,
        year: int,
        poster_file_id: str | None,
        files: list[ParsedFile],
        created_by: int,
        status: str,
    ) -> dict:
        movie_id = await generate_movie_id(self._movie_repo)
        now = datetime.now(timezone.utc)
        movie = {
            "movie_id": movie_id,
            "title": title,
            "normalized_title": normalize_title(title),
            "year": year,
            "poster_file_id": poster_file_id,
            "status": status,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }
        await self._movie_repo.insert_one(movie)

        if files:
            file_docs = []
            for f in files:
                file_docs.append({
                    "movie_id": movie_id,
                    "file_id": f.file_id,
                    "file_unique_id": f.file_unique_id,
                    "file_name": f.display_name or f.original_filename,
                    "file_size": f.file_size,
                    "quality": f.quality,
                    "part": 0,
                    "mime_type": f.mime_type,
                    "created_at": now,
                })
            await self._movie_file_repo.insert_many(file_docs)

        logger.info(
            "Movie %s created with status=%s, movie_id=%s, files=%d",
            title, status, movie_id, len(files),
        )
        return movie

    async def save_draft(
        self,
        title: str,
        year: int,
        poster_file_id: str | None,
        files: list[ParsedFile],
        created_by: int,
    ) -> dict:
        return await self.create_movie_document(
            title=title,
            year=year,
            poster_file_id=poster_file_id,
            files=files,
            created_by=created_by,
            status="draft",
        )

    async def publish_movie(
        self,
        title: str,
        year: int,
        poster_file_id: str | None,
        files: list[ParsedFile],
        created_by: int,
    ) -> dict:
        return await self.create_movie_document(
            title=title,
            year=year,
            poster_file_id=poster_file_id,
            files=files,
            created_by=created_by,
            status="public",
        )

    async def duplicate_check(self, title: str, year: int) -> bool:
        normalized = normalize_title(title)
        return await self._movie_repo.exists(
            {"normalized_title": normalized, "year": year}
        )

    async def find_duplicate(self, title: str, year: int) -> dict | None:
        """Return the full duplicate movie document if one exists."""
        normalized = normalize_title(title)
        docs = await self._movie_repo.find_many(
            {"normalized_title": normalized, "year": year},
            limit=1,
        )
        return docs[0] if docs else None

    async def get_movie_by_id(self, movie_id: str) -> dict | None:
        return await self._movie_repo.find_by_movie_id(movie_id)
