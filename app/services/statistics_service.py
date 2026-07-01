from __future__ import annotations

from datetime import datetime, timezone
from logging import getLogger
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.database.collections import collections
from app.database.manager import db_manager

logger = getLogger(__name__)


class StatisticsService:
    _STATS_COLLECTION = collections.STATISTICS

    def __init__(self) -> None:
        self._collection = None

    @property
    def collection(self):
        if self._collection is not None:
            return self._collection
        return db_manager.db[self._STATS_COLLECTION]

    @collection.setter
    def collection(self, value):
        self._collection = value

    async def increment(
        self,
        key: str,
        amount: int = 1,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filter_ = {"key": key, "date": today}
        update = {"$inc": {"value": amount}}
        result = await self.collection.update_one(filter_, update, session=session)
        if result.modified_count == 0:
            await self.collection.update_one(
                {"key": key},
                {"$inc": {"value": amount}},
                upsert=True,
                session=session,
            )

    async def set(
        self,
        key: str,
        value: Any,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        await self.collection.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True,
            session=session,
        )

    async def get(self, key: str) -> Any | None:
        doc = await self.collection.find_one({"key": key})
        return doc["value"] if doc else None

    async def get_all(self) -> dict[str, Any]:
        docs = await self.collection.find({}).to_list(length=1000)
        return {doc["key"]: doc.get("value") for doc in docs}

    async def update_on_publish(
        self,
        movie_id: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        await self.increment("total_movies", session=session)
        await self.increment("public_movies", session=session)
        await self.increment(f"published_{today}", session=session)
        await self.set("last_published_movie", movie_id, session=session)

    async def update_on_draft(
        self,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        await self.increment("draft_movies", session=session)
