import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("MongoDB is not initialized")
    return database


def get_collections() -> dict:
    db = get_db()
    return {
        "sources": db["sources"],
        "news": db["news"],
        "crawl_logs": db["crawl_logs"],
        "crawl_locks": db["crawl_locks"],
    }


async def connect_to_mongo() -> None:
    global client, database
    client = AsyncIOMotorClient(
        settings.mongodb_uri,
        tlsCAFile=certifi.where(),
        # Atlas M0 free tier: giới hạn pool để không bị từ chối kết nối
        maxPoolSize=10,
        minPoolSize=1,
        serverSelectionTimeoutMS=10_000,
        connectTimeoutMS=10_000,
        socketTimeoutMS=30_000,
        # tz_aware=True: datetime trả về kèm UTC tzinfo, FastAPI serialize có "+00:00"
        # để frontend (JS) parse đúng và quy đổi sang giờ Việt Nam (GMT+7) chính xác.
        tz_aware=True,
    )
    database = client[settings.mongodb_db]
    await create_indexes()


async def close_mongo_connection() -> None:
    if client is not None:
        client.close()


async def create_indexes() -> None:
    collections = get_collections()
    await collections["sources"].create_index("base_url", unique=True)
    await collections["sources"].create_index([("created_at", -1)])

    await collections["news"].create_index("source_url", unique=True)
    await collections["news"].create_index([("published_at", -1)])
    # Compound index phục vụ filter theo nguồn + sort theo ngày — query phổ biến nhất.
    await collections["news"].create_index([("source_id", 1), ("published_at", -1)])
    await collections["news"].create_index([("title", "text"), ("content", "text")])

    await collections["crawl_logs"].create_index([("crawled_at", -1)])

    # crawl_locks: TTL index — document tự xoá sau khi hết hạn → unlock tự động
    # nếu instance giữ lock crash. expireAfterSeconds=0 nghĩa là dùng giá trị
    # `expires_at` trong document làm thời điểm hết hạn.
    await collections["crawl_locks"].create_index(
        "expires_at", expireAfterSeconds=0
    )
