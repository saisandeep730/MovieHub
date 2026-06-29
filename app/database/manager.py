from logging import getLogger

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure

from app.config import settings
from app.database.indexes import IndexDefinitions

logger = getLogger(__name__)


class DatabaseManager:
    """Manages the MongoDB async connection lifecycle with index management."""

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        logger.info("Connecting to MongoDB at %s", settings.MONGODB_URI)
        self._client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
        self._db = self._client[settings.DATABASE_NAME]
        await self._client.admin.command("ping")
        logger.info("MongoDB connection established")

    async def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

    async def startup(self) -> None:
        await self.connect()
        await self.ensure_indexes()

    async def shutdown(self) -> None:
        await self.disconnect()

    async def health_check(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    async def ensure_indexes(self) -> None:
        logger.info("Ensuring MongoDB indexes")
        for collection_name, index_models in IndexDefinitions.all_indexes().items():
            collection = self.db[collection_name]
            existing_indexes = await collection.index_information()
            existing_by_key = {}
            existing_has_text = False
            for existing_name, info in existing_indexes.items():
                if existing_name == "_id_":
                    continue
                key_tuples = info["key"]
                key_frozen = frozenset(key_tuples)
                existing_by_key[key_frozen] = existing_name
                if any(v == "text" for _, v in key_tuples):
                    existing_has_text = True

            for index_model in index_models:
                doc = index_model.document
                key_frozen = frozenset(doc["key"].items())
                index_name = doc.get("name", "unknown")

                if key_frozen in existing_by_key:
                    logger.warning(
                        "Index %s already exists in collection %s",
                        index_name, collection_name,
                    )
                    continue

                desired_has_text = any(v == "text" for v in doc["key"].values())
                if desired_has_text and existing_has_text:
                    logger.warning(
                        "Text index %s skipped — another text index already exists in %s",
                        index_name, collection_name,
                    )
                    continue

                try:
                    await collection.create_indexes([index_model])
                    logger.debug("Created index %s on %s", index_name, collection_name)
                except OperationFailure as e:
                    logger.warning(
                        "Could not create index %s on %s: %s",
                        index_name, collection_name, str(e),
                    )
                except Exception:
                    logger.exception(
                        "Failed to create index %s on %s",
                        index_name, collection_name,
                    )
        logger.info("All indexes ensured")

    async def session(self) -> AsyncIOMotorClientSession:
        return await self.client.start_session()

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() or startup() first.")
        return self._db

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            raise RuntimeError("Database not connected. Call connect() or startup() first.")
        return self._client


db_manager = DatabaseManager()
