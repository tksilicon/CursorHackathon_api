"""MongoDB connection."""
from pymongo import MongoClient
from pymongo.database import Database

from backend.config import MONGODB_URI, DB_NAME

_client: MongoClient | None = None


def get_db() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client[DB_NAME]
