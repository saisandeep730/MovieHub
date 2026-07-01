from __future__ import annotations

from datetime import datetime, timezone
from logging import getLogger
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.database import db_manager
from app.events import DraftSavedEvent, MovieUploadedEvent, event_bus
from app.repositories import (
    CountersRepositoryProtocol,
    MovieFileRepositoryProtocol,
    MovieRepositoryProtocol,
)
from app.services.statistics_service import StatisticsService
from app.utils import normalize_title
from app.utils.filename_types import ParsedFile

logger = getLogger(__name__)


class UploadService:
    """Coordinates the multi-step movie upload workflow with transactions."""

    def __init__(
        self,
        movie_repo: MovieRepositoryProtocol,
        movie_file_repo: MovieFileRepositoryProtocol,
        counters_repo: CountersRepositoryProtocol,
        statistics_service: StatisticsService,
    ) -> None:
        self._movie_repo = movie_repo
        self._movie_file_repo = movie_file_repo
        self._counters_repo = counters_repo
        self._statistics_service = statistics_service

    async def _generate_movie_id(self) -> str:
        """Atomic movie ID generation using MongoDB counter."""
        seq = await self._counters_repo.get_next_sequence("movie_id")
        return f"MH{seq:06d}"

    def _build_file_docs(
        self, movie_id: str, files: list[ParsedFile], now: datetime,
    ) -> list[dict]:
        docs = []
        for f in files:
            docs.append({
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
        return docs

    async def save_draft(
        self,
        title: str,
        year: int,
        poster_file_id: str | None,
        files: list[ParsedFile],
        created_by: int,
    ) -> dict:
        """Save a movie as draft — no transaction needed."""
        movie_id = await self._generate_movie_id()
        now = datetime.now(timezone.utc)
        movie = {
            "movie_id": movie_id,
            "title": title,
            "normalized_title": normalize_title(title),
            "year": year,
            "poster_file_id": poster_file_id,
            "status": "draft",
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }
        await self._movie_repo.insert_one(movie)

        if files:
            file_docs = self._build_file_docs(movie_id, files, now)
            await self._movie_file_repo.insert_many(file_docs)

        await self._statistics_service.update_on_draft()
        await event_bus.publish(DraftSavedEvent(
            movie_id=movie_id,
            title=title,
            year=year,
            created_by=created_by,
        ))

        logger.info(
            "Draft saved: %s, movie_id=%s, files=%d",
            title, movie_id, len(files),
        )
        return movie

    async def publish_movie(
        self,
        title: str,
        year: int,
        poster_file_id: str | None,
        files: list[ParsedFile],
        created_by: int,
    ) -> dict:
        """Publish a movie using a MongoDB transaction for atomicity."""
        session = await db_manager.session()
        movie_id = await self._generate_movie_id()
        now = datetime.now(timezone.utc)

        try:
            session.start_transaction()

            movie = {
                "movie_id": movie_id,
                "title": title,
                "normalized_title": normalize_title(title),
                "year": year,
                "poster_file_id": poster_file_id,
                "status": "public",
                "created_by": created_by,
                "created_at": now,
                "updated_at": now,
            }
            await self._movie_repo.insert_one(movie, session=session)

            if files:
                file_docs = self._build_file_docs(movie_id, files, now)
                await self._movie_file_repo.insert_many(file_docs, session=session)

            await self._statistics_service.update_on_publish(movie_id, session=session)

            await session.commit_transaction()
        except Exception:
            logger.exception("Publish transaction failed, aborting")
            await session.abort_transaction()
            raise

        await event_bus.publish(MovieUploadedEvent(
            movie_id=movie_id,
            title=title,
            year=year,
            created_by=created_by,
            status="public",
        ))

        logger.info(
            "Movie published: %s, movie_id=%s, files=%d",
            title, movie_id, len(files),
        )
        return movie

    async def merge_movie(
        self,
        existing_movie: dict,
        new_files: list[ParsedFile],
        updated_by: int,
    ) -> dict:
        """Merge new files into an existing movie (skip duplicates by file_unique_id)."""
        movie_id = existing_movie["movie_id"]
        now = datetime.now(timezone.utc)

        existing_file_docs = await self._movie_file_repo.find_by_movie_id(movie_id)
        existing_unique_ids = {
            f["file_unique_id"] for f in existing_file_docs
        }

        files_to_add = [
            f for f in new_files
            if f.file_unique_id not in existing_unique_ids
        ]

        if not files_to_add:
            logger.info("Merge: no new files to add for %s", movie_id)
            return existing_movie

        file_docs = self._build_file_docs(movie_id, files_to_add, now)
        await self._movie_file_repo.insert_many(file_docs)

        await self._movie_repo.update_one(
            {"movie_id": movie_id},
            {"updated_at": now},
        )

        logger.info(
            "Merged %d files into movie %s (%s)",
            len(files_to_add), movie_id, existing_movie.get("title"),
        )
        existing_movie["_merged_files"] = len(files_to_add)
        existing_movie["_skipped_files"] = len(new_files) - len(files_to_add)
        return existing_movie

    async def replace_movie(
        self,
        existing_movie: dict,
        new_title: str,
        new_year: int,
        new_poster_file_id: str | None,
        new_files: list[ParsedFile],
        updated_by: int,
    ) -> dict:
        """Replace all data of an existing movie."""
        movie_id = existing_movie["movie_id"]
        now = datetime.now(timezone.utc)

        await self._movie_file_repo.delete_by_movie_id(movie_id)

        await self._movie_repo.update_one(
            {"movie_id": movie_id},
            {
                "title": new_title,
                "normalized_title": normalize_title(new_title),
                "year": new_year,
                "poster_file_id": new_poster_file_id,
                "updated_at": now,
            },
        )

        if new_files:
            file_docs = self._build_file_docs(movie_id, new_files, now)
            await self._movie_file_repo.insert_many(file_docs)

        logger.info(
            "Replaced movie %s (%s), new files=%d",
            movie_id, new_title, len(new_files),
        )
        existing_movie["title"] = new_title
        existing_movie["year"] = new_year
        return existing_movie

    async def duplicate_check(self, title: str, year: int) -> bool:
        normalized = normalize_title(title)
        return await self._movie_repo.exists(
            {"normalized_title": normalized, "year": year}
        )

    async def find_duplicate(self, title: str, year: int) -> dict | None:
        normalized = normalize_title(title)
        docs = await self._movie_repo.find_many(
            {"normalized_title": normalized, "year": year},
            limit=1,
        )
        return docs[0] if docs else None

    async def get_movie_by_id(self, movie_id: str) -> dict | None:
        return await self._movie_repo.find_by_movie_id(movie_id)

    async def get_drafts(self, limit: int = 50) -> list[dict]:
        return await self._movie_repo.find_many(
            {"status": "draft"},
            limit=limit,
            sort=[("updated_at", -1)],
        )

    async def publish_draft(self, movie_id: str, published_by: int) -> dict | None:
        movie = await self._movie_repo.find_by_movie_id(movie_id)
        if not movie or movie.get("status") != "draft":
            return None
        now = datetime.now(timezone.utc)
        await self._movie_repo.update_one(
            {"movie_id": movie_id},
            {"status": "public", "updated_at": now},
        )
        await event_bus.publish(MovieUploadedEvent(
            movie_id=movie_id,
            title=movie["title"],
            year=movie.get("year", 0),
            created_by=published_by,
            status="public",
        ))
        movie["status"] = "public"
        movie["updated_at"] = now
        logger.info("Draft %s published by user %d", movie_id, published_by)
        return movie

    async def delete_movie(self, movie_id: str) -> bool:
        movie = await self._movie_repo.find_by_movie_id(movie_id)
        if not movie:
            return False
        await self._movie_file_repo.delete_by_movie_id(movie_id)
        await self._movie_repo.delete_one({"movie_id": movie_id})
        logger.info("Movie %s deleted", movie_id)
        return True
