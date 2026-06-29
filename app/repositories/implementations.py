from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.database import BaseRepository, collections, db_manager


class MovieRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.MOVIES)

    async def find_by_movie_id(self, movie_id: str) -> dict | None:
        return await self.find_one({"movie_id": movie_id})

    async def find_by_normalized_title(self, title: str) -> dict | None:
        return await self.find_one({"normalized_title": title})

    async def search(self, query: str, skip: int, limit: int) -> list[dict]:
        return await self.find_many(
            {"$text": {"$search": query}},
            skip=skip, limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_latest(self, status: str, skip: int, limit: int) -> list[dict]:
        return await self.find_many(
            {"status": status},
            skip=skip, limit=limit,
            sort=[("created_at", -1)],
        )


class MovieFileRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.MOVIE_FILES)

    async def find_by_movie_id(self, movie_id: str) -> list[dict]:
        return await self.find_many({"movie_id": movie_id}, limit=100)

    async def find_by_file_unique_id(self, file_unique_id: str) -> dict | None:
        return await self.find_one({"file_unique_id": file_unique_id})

    async def delete_by_movie_id(self, movie_id: str) -> int:
        return await self.delete_many({"movie_id": movie_id})


class SettingsRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.SETTINGS)

    async def get(self, key: str) -> dict | None:
        return await self.find_one({"key": key})

    async def set(self, key: str, value: Any, updated_by: int | None = None) -> None:
        update: dict[str, Any] = {"value": value}
        if updated_by is not None:
            update["updated_by"] = updated_by
        existing = await self.get(key)
        if existing:
            await self.update_one({"key": key}, update)
        else:
            doc: dict[str, Any] = {"key": key, "value": value}
            if updated_by is not None:
                doc["updated_by"] = updated_by
            await self.insert_one(doc)

    async def get_all(self) -> list[dict]:
        return await self.find_many({}, limit=500)


class RequestRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.REQUESTS)

    async def find_by_movie_name(self, movie_name: str) -> dict | None:
        return await self.find_one({"movie_name": movie_name})

    async def find_by_user_id(self, user_id: int) -> list[dict]:
        return await self.find_many({"user_id": user_id}, sort=[("created_at", -1)])

    async def find_pending(self, skip: int, limit: int) -> list[dict]:
        return await self.find_many({"fulfilled": False}, skip=skip, limit=limit, sort=[("created_at", -1)])

    async def mark_fulfilled(self, request_id: str, movie_id: str) -> int:
        return await self.update_one(
            {"_id": request_id},
            {"fulfilled": True, "fulfilled_movie_id": movie_id},
        )

    async def increment_count(self, request_id: str) -> None:
        await self.collection.update_one({"_id": request_id}, {"$inc": {"count": 1}})


class UserRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.USERS)

    async def upsert_user(self, user_data: dict) -> None:
        user_id = user_data.pop("user_id", None)
        if not user_id:
            return
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True,
        )

    async def find_by_user_id(self, user_id: int) -> dict | None:
        return await self.find_one({"user_id": user_id})

    async def find_active(self, skip: int, limit: int) -> list[dict]:
        return await self.find_many({"is_active": True}, skip=skip, limit=limit, sort=[("created_at", -1)])


class AdminRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.ADMINS)

    async def find_by_user_id(self, user_id: int) -> dict | None:
        return await self.find_one({"user_id": user_id})

    async def find_all_active(self) -> list[dict]:
        return await self.find_many({"is_active": True}, limit=200)

    async def is_admin(self, user_id: int) -> bool:
        return await self.exists({"user_id": user_id, "is_active": True})


class BroadcastRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.BROADCASTS)

    async def find_by_status(self, status: str) -> list[dict]:
        return await self.find_many({"status": status}, limit=50, sort=[("created_at", -1)])

    async def update_progress(self, broadcast_id: str, success: int, fail: int) -> None:
        await self.update_one(
            {"_id": broadcast_id},
            {"success_count": success, "fail_count": fail},
        )


class BackupRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.BACKUPS)

    async def find_latest(self) -> dict | None:
        results = await self.find_many({}, limit=1, sort=[("created_at", -1)])
        return results[0] if results else None

    async def find_by_type(self, type_: str, limit: int) -> list[dict]:
        return await self.find_many({"type": type_}, limit=limit, sort=[("created_at", -1)])


class HealthRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.HEALTH)

    async def find_latest_checks(self, component: str, limit: int) -> list[dict]:
        return await self.find_many({"component": component}, limit=limit, sort=[("checked_at", -1)])


class SessionRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(db_manager, collections.SESSIONS)

    async def find_by_user_id(self, user_id: int) -> dict | None:
        return await self.find_one({"user_id": user_id})

    async def cleanup_expired(self) -> int:
        result = await self.collection.delete_many({"expires_at": {"$lt": datetime.now(timezone.utc)}})
        return result.deleted_count
