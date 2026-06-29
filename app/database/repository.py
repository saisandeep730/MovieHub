from logging import getLogger
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorCollection
from pymongo import ReturnDocument

from app.database.manager import DatabaseManager

logger = getLogger(__name__)


class BaseRepository:
    """Production-ready base repository with full CRUD and transaction support."""

    def __init__(self, db_manager: DatabaseManager, collection_name: str) -> None:
        self._db_manager = db_manager
        self._collection_name = collection_name

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self._db_manager.db[self._collection_name]

    async def insert_one(self, document: dict, session: AsyncIOMotorClientSession | None = None) -> str:
        result = await self.collection.insert_one(document, session=session)
        return str(result.inserted_id)

    async def insert_many(self, documents: list[dict], session: AsyncIOMotorClientSession | None = None) -> list[str]:
        result = await self.collection.insert_many(documents, session=session)
        return [str(oid) for oid in result.inserted_ids]

    async def find_one(
        self,
        filter_: dict,
        projection: dict | None = None,
        session: AsyncIOMotorClientSession | None = None,
    ) -> dict | None:
        return await self.collection.find_one(filter_, projection, session=session)

    async def find_many(
        self,
        filter_: dict,
        projection: dict | None = None,
        skip: int = 0,
        limit: int = 20,
        sort: list[tuple[str, int]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[dict]:
        cursor = self.collection.find(filter_, projection, skip=skip, session=session).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)

    async def find_one_and_update(
        self,
        filter_: dict,
        update: dict,
        return_document: bool = True,
        session: AsyncIOMotorClientSession | None = None,
    ) -> dict | None:
        return await self.collection.find_one_and_update(
            filter_,
            update,
            return_document=ReturnDocument.AFTER if return_document else ReturnDocument.BEFORE,
            session=session,
        )

    async def update_one(
        self,
        filter_: dict,
        update: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        result = await self.collection.update_one(filter_, {"$set": update}, session=session)
        return result.modified_count

    async def update_many(
        self,
        filter_: dict,
        update: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        result = await self.collection.update_many(filter_, {"$set": update}, session=session)
        return result.modified_count

    async def delete_one(
        self,
        filter_: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        result = await self.collection.delete_one(filter_, session=session)
        return result.deleted_count

    async def delete_many(
        self,
        filter_: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        result = await self.collection.delete_many(filter_, session=session)
        return result.deleted_count

    async def count(self, filter_: dict | None = None, session: AsyncIOMotorClientSession | None = None) -> int:
        return await self.collection.count_documents(filter_ or {}, session=session)

    async def exists(self, filter_: dict, session: AsyncIOMotorClientSession | None = None) -> bool:
        return await self.collection.find_one(filter_, {"_id": 1}, session=session) is not None

    async def aggregate(
        self,
        pipeline: list[dict[str, Any]],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[dict]:
        cursor = self.collection.aggregate(pipeline, session=session)
        return await cursor.to_list(length=None)

    async def distinct(self, key: str, filter_: dict | None = None) -> list[Any]:
        return await self.collection.distinct(key, filter_ or {})
