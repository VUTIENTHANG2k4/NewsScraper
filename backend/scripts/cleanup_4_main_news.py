"""One-off: xoá bài cũ của 4 nguồn lớn để crawl lại sạch."""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.mongo import close_mongo_connection, connect_to_mongo, get_collections


async def main() -> None:
    await connect_to_mongo()
    try:
        c = get_collections()
        result = await c["news"].delete_many(
            {"source_name": {"$in": ["VnExpress", "Tuoi Tre", "Thanh Nien", "Dan Tri"]}}
        )
        print(f"Deleted {result.deleted_count} old news records.")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
