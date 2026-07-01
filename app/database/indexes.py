from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel

from app.database.collections import collections


class IndexDefinitions:
    """All required MongoDB index definitions, grouped by collection."""

    MOVIES = [
        IndexModel([("movie_id", ASCENDING)], unique=True),
        IndexModel([("normalized_title", ASCENDING)]),
        IndexModel([("title", TEXT), ("normalized_title", TEXT)]),
        IndexModel([("year", ASCENDING)]),
        IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("status", ASCENDING), ("normalized_title", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ]

    MOVIE_FILES = [
        IndexModel([("movie_id", ASCENDING)]),
        IndexModel([("file_unique_id", ASCENDING)], unique=True),
    ]

    REQUESTS = [
        IndexModel([("movie_name", ASCENDING)]),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ]

    USERS = [
        IndexModel([("user_id", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
    ]

    ADMINS = [
        IndexModel([("user_id", ASCENDING)], unique=True),
    ]

    SETTINGS = [
        IndexModel([("key", ASCENDING)], unique=True),
    ]

    STATISTICS = [
        IndexModel([("key", ASCENDING)], unique=True),
        IndexModel([("date", ASCENDING)]),
    ]

    BROADCASTS = [
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("status", ASCENDING)]),
    ]

    BACKUPS = [
        IndexModel([("created_at", DESCENDING)]),
    ]

    HEALTH = [
        IndexModel([("created_at", DESCENDING)]),
    ]

    SESSIONS = [
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),
    ]

    COUNTERS = [
        IndexModel([("_id", ASCENDING)]),
    ]

    @classmethod
    def all_indexes(cls) -> dict[str, list[IndexModel]]:
        return {
            collections.MOVIES: cls.MOVIES,
            collections.MOVIE_FILES: cls.MOVIE_FILES,
            collections.REQUESTS: cls.REQUESTS,
            collections.USERS: cls.USERS,
            collections.ADMINS: cls.ADMINS,
            collections.SETTINGS: cls.SETTINGS,
            collections.STATISTICS: cls.STATISTICS,
            collections.BROADCASTS: cls.BROADCASTS,
            collections.BACKUPS: cls.BACKUPS,
            collections.HEALTH: cls.HEALTH,
            collections.SESSIONS: cls.SESSIONS,
            collections.COUNTERS: cls.COUNTERS,
        }
