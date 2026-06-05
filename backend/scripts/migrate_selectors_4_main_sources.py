"""
Migration script: PATCH selectors cho 4 nguồn lớn đã tồn tại trong DB.

Lý do: `seed_sources_if_empty()` chỉ seed khi collection rỗng. Trên DB đã chạy
một thời gian (có dữ liệu), seed mới sẽ không áp. Script này áp selectors
đã verify (xem scripts/verify_selectors.py) cho VnExpress / Tuoi Tre /
Thanh Nien / Dan Tri — match theo `name` (idempotent, chạy lại nhiều lần OK).

Chạy:
    docker compose exec backend python scripts/migrate_selectors_4_main_sources.py
"""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.mongo import close_mongo_connection, connect_to_mongo, get_collections


# Các selector đã verify qua scripts/verify_selectors.py.
# Lưu ý: published_at để trống cho 3 nguồn — engine sẽ tự dùng fallback meta
# tag chuẩn schema.org (article:published_time, time[datetime] …).
UPDATES = [
    {
        "name": "VnExpress",
        "selectors": {
            "article_list": "h3.title-news a, h2.title-news a",
            "title": "h1.title-detail",
            "author": ".author",
            "content": "article.fck_detail",
            "published_at": ".date",
            "image": 'meta[property="og:image"]',
            "date_format": "",
        },
    },
    {
        "name": "Tuoi Tre",
        "selectors": {
            "article_list": "h3.box-title-news a, a.box-category-link-title",
            "title": "h1.article-title, h1.detail-title",
            "author": ".author-info",
            "content": ".detail-content",
            "published_at": "",
            "image": 'meta[property="og:image"]',
            "date_format": "",
        },
    },
    {
        "name": "Thanh Nien",
        "selectors": {
            "article_list": (
                "h2.box-title-text a, h3.box-title-text a, "
                "h2.story__title a, h3.story__title a, "
                ".box-category-item a.box-category-link-title"
            ),
            "title": "h1.detail-title, h1.story__title",
            "author": "",
            "content": ".detail-content, .story__detail",
            "published_at": "",
            "image": 'meta[property="og:image"]',
            "date_format": "",
        },
    },
    {
        "name": "Dan Tri",
        "selectors": {
            "article_list": "h3.article-title a, h2.article-title a",
            "title": "h1.title-page, h1.singular-title",
            "author": ".author-name",
            "content": ".singular-content, .dt-news__content",
            "published_at": "",
            "image": 'meta[property="og:image"]',
            "date_format": "",
        },
    },
]


async def main() -> None:
    await connect_to_mongo()
    try:
        collections = get_collections()
        sources = collections["sources"]

        print(f"Migration: cập nhật selectors cho {len(UPDATES)} nguồn lớn...")
        for item in UPDATES:
            result = await sources.update_one(
                {"name": item["name"]},
                {"$set": {"selectors": item["selectors"]}},
            )
            tag = "UPDATED" if result.modified_count else (
                "MATCHED-NO-CHANGE" if result.matched_count else "NOT-FOUND"
            )
            print(f"  - {item['name']:14s} → {tag}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
