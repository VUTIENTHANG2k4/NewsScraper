from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from db.mongo import get_collections
from scraper.engine import crawl_active_sources, crawl_one_source
from scraper.extractor import extract_attribute, extract_text
from scraper.fetcher import fetch_html

router = APIRouter(prefix="/crawl", tags=["crawl"])


class PreviewSelectors(BaseModel):
    title: str = ""
    author: str = ""
    content: str = ""
    published_at: str = ""
    image: str = ""


class CrawlPreviewRequest(BaseModel):
    url: HttpUrl
    selector_type: Literal["css", "xpath"] = "css"
    selectors: PreviewSelectors


@router.post("/trigger")
async def trigger_all_crawl() -> dict:
    logs = await crawl_active_sources()
    return {"message": "Đã crawl toàn bộ nguồn active", "results": logs}


@router.post("/trigger/{source_id}")
async def trigger_one_crawl(source_id: str) -> dict:
    try:
        result = await crawl_one_source(source_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Lỗi crawl: {error}") from error

    return {"message": "Đã crawl nguồn thành công", "result": result}


@router.post("/preview")
async def crawl_preview(payload: CrawlPreviewRequest) -> dict:
    html = await fetch_html(str(payload.url))

    title = extract_text(html, payload.selectors.title, payload.selector_type)
    author = extract_text(html, payload.selectors.author, payload.selector_type)
    content = extract_text(html, payload.selectors.content, payload.selector_type)
    published_at_raw = extract_text(
        html, payload.selectors.published_at, payload.selector_type
    )
    image_url = extract_attribute(
        html, payload.selectors.image, "content", payload.selector_type
    ) or extract_attribute(html, payload.selectors.image, "src", payload.selector_type)

    if content:
        content = content[:200]

    return {
        "title": title,
        "author": author,
        "content": content,
        "published_at": published_at_raw or datetime.now(UTC).isoformat(),
        "image_url": image_url,
    }
