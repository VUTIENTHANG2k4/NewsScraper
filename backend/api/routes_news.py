import asyncio
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query, Response

from db.mongo import get_collections

router = APIRouter(tags=["news"])

# Các field cần thiết cho ArticleCard — loại content (50KB/bài) khỏi list response
_NEWS_LIST_PROJECTION = {
    "content": 0,
}


def _serialize_news(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "source_id": document.get("source_id"),
        "source_name": document.get("source_name"),
        "source_url": document.get("source_url"),
        "title": document.get("title"),
        "author": document.get("author"),
        "image_url": document.get("image_url"),
        "published_at": document.get("published_at"),
        "created_at": document.get("created_at"),
    }


@router.get("/news")
async def get_news(
    response: Response,
    q: str | None = None,
    from_date: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
    source_id: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    response.headers["Cache-Control"] = "public, max-age=60"
    collections = get_collections()
    query: dict = {}

    if q:
        query["$text"] = {"$search": q}

    if from_date or to:
        date_query: dict = {}
        if from_date:
            date_query["$gte"] = from_date
        if to:
            date_query["$lte"] = to
        query["published_at"] = date_query

    if source_id:
        # source_id được lưu trong news dưới dạng string (hex của ObjectId).
        # Validate định dạng để tránh query rác, sau đó so khớp string.
        try:
            ObjectId(source_id)
        except (InvalidId, TypeError) as error:
            raise HTTPException(status_code=400, detail="source_id không hợp lệ") from error
        query["source_id"] = source_id

    skip = (page - 1) * limit

    # count_documents và find chạy song song — tiết kiệm 1 Atlas round-trip (~50-100ms)
    total, docs = await asyncio.gather(
        collections["news"].count_documents(query),
        collections["news"]
        .find(query, _NEWS_LIST_PROJECTION)
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit),
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [_serialize_news(doc) for doc in docs],
    }


@router.get("/stats")
async def get_stats(response: Response) -> dict:
    response.headers["Cache-Control"] = "public, max-age=60"
    collections = get_collections()

    total_news, active_sources, latest_log = await asyncio.gather(
        collections["news"].count_documents({}),
        collections["sources"].count_documents({"is_active": True}),
        collections["crawl_logs"].find_one(sort=[("crawled_at", -1)]),
    )

    return {
        "total_news": total_news,
        "active_sources": active_sources,
        "last_crawl_at": latest_log.get("crawled_at") if latest_log else None,
    }
