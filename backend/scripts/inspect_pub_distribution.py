"""Inspect published_at distribution để biết bao nhiều bài rớt now()."""

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.mongo import close_mongo_connection, connect_to_mongo, get_collections


async def main() -> None:
    await connect_to_mongo()
    try:
        c = get_collections()
        # "Coi như rớt now()" = published_at trong khoảng 5 phút quanh thời điểm
        # crawl gần nhất. Heuristic này không hoàn hảo nhưng đủ để debug.
        for name in ["VnExpress", "Tuoi Tre", "Thanh Nien", "Dan Tri"]:
            total = await c["news"].count_documents({"source_name": name})
            recent_5min = await c["news"].count_documents(
                {
                    "source_name": name,
                    "published_at": {
                        "$gte": datetime.now(UTC) - timedelta(minutes=5)
                    },
                }
            )
            print(f"{name:14s} total={total:4d} | published_at trong 5 phút gần đây = {recent_5min}")

            sample = await c["news"].find({"source_name": name}).limit(3).to_list(3)
            for s in sample:
                pa = s.get("published_at")
                ca = s.get("created_at")
                url = s.get("source_url", "")[:70]
                # Hiển thị diff giữa published_at và created_at: nếu ~0 → rớt now()
                diff = (ca - pa).total_seconds() if pa and ca else None
                print(f"  diff(created-published)={diff}s  pa={pa}  url={url}")
            print()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
