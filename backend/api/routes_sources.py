from datetime import UTC, datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from db.mongo import get_collections
from models.source import SourceCreate, SourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


def _serialize_source(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "name": document["name"],
        "base_url": document["base_url"],
        "crawl_type": document["crawl_type"],
        "selector_type": document["selector_type"],
        "selectors": document.get("selectors", {}),
        "is_active": document.get("is_active", True),
        "last_crawled": document.get("last_crawled"),
        "created_at": document.get("created_at"),
    }


@router.get("")
async def get_sources() -> list[dict]:
    collections = get_collections()
    docs = await collections["sources"].find({}).sort("created_at", -1).to_list(length=500)
    return [_serialize_source(doc) for doc in docs]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_source(payload: SourceCreate) -> dict:
    collections = get_collections()
    document = {
        "name": payload.name,
        "base_url": str(payload.base_url),
        "crawl_type": payload.crawl_type,
        "selector_type": payload.selector_type,
        "selectors": payload.selectors.model_dump(),
        "is_active": True,
        "last_crawled": None,
        "created_at": datetime.now(UTC),
    }
    try:
        result = await collections["sources"].insert_one(document)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="URL nguồn đã tồn tại") from error

    created = await collections["sources"].find_one({"_id": result.inserted_id})
    return _serialize_source(created)


@router.patch("/{source_id}")
async def update_source(source_id: str, payload: SourceUpdate) -> dict:
    collections = get_collections()
    try:
        object_id = ObjectId(source_id)
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="source_id không hợp lệ") from error

    update_data = payload.model_dump(exclude_none=True)
    if "selectors" in update_data and payload.selectors is not None:
        update_data["selectors"] = payload.selectors.model_dump()

    if not update_data:
        source = await collections["sources"].find_one({"_id": object_id})
        if source is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy nguồn")
        return _serialize_source(source)

    result = await collections["sources"].update_one(
        {"_id": object_id},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy nguồn")

    updated = await collections["sources"].find_one({"_id": object_id})
    return _serialize_source(updated)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: str) -> None:
    collections = get_collections()
    try:
        object_id = ObjectId(source_id)
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="source_id không hợp lệ") from error

    result = await collections["sources"].delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy nguồn")
