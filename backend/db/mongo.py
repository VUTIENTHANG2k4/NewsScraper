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
    }


async def connect_to_mongo() -> None:
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_uri)
    database = client[settings.mongodb_db]
    await create_indexes()


async def close_mongo_connection() -> None:
    if client is not None:
        client.close()


async def create_indexes() -> None:
    collections = get_collections()
    await collections["sources"].create_index("base_url", unique=True)
    await collections["news"].create_index("source_url", unique=True)
    await collections["news"].create_index([("published_at", -1)])
    await collections["news"].create_index([("title", "text"), ("content", "text")])
    await collections["crawl_logs"].create_index([("crawled_at", -1)])
