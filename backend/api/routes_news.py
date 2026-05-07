from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Query

from db.mongo import get_collections

router = APIRouter(tags=["news"])


def _serialize_news(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "source_id": document.get("source_id"),
        "source_name": document.get("source_name"),
        "source_url": document.get("source_url"),
        "title": document.get("title"),
        "author": document.get("author"),
        "content": document.get("content"),
        "image_url": document.get("image_url"),
        "published_at": document.get("published_at"),
        "created_at": document.get("created_at"),
    }


@router.get("/news")
async def get_news(
    q: str | None = None,
    from_date: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
    source_id: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
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
        try:
            ObjectId(source_id)
        except Exception:
            # source_id được lưu dạng string để đơn giản hóa dedup và response.
            pass
        query["source_id"] = source_id

    total = await collections["news"].count_documents(query)
    skip = (page - 1) * limit
    docs = (
        await collections["news"]
        .find(query)
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [_serialize_news(doc) for doc in docs],
    }


@router.get("/stats")
async def get_stats() -> dict:
    collections = get_collections()
    total_news = await collections["news"].count_documents({})
    active_sources = await collections["sources"].count_documents({"is_active": True})
    latest_log = await collections["crawl_logs"].find_one(sort=[("crawled_at", -1)])
    return {
        "total_news": total_news,
        "active_sources": active_sources,
        "last_crawl_at": latest_log.get("crawled_at") if latest_log else None,
    }
