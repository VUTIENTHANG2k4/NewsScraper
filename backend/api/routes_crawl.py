from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from api.deps import require_api_key
from scraper.engine import crawl_active_sources, crawl_one_source
from scraper.extractor import extract_attribute, extract_text, parse_html
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


@router.post("/trigger", dependencies=[Depends(require_api_key)])
async def trigger_all_crawl() -> dict:
    result = await crawl_active_sources()
    if not result["acquired"]:
        return {
            "message": result["skipped_reason"]
            or "Đã có instance khác đang crawl, bỏ qua lần này.",
            "results": [],
            "skipped": True,
        }
    if not result["logs"]:
        return {
            "message": result["skipped_reason"] or "Không có nguồn active để crawl.",
            "results": [],
            "skipped": True,
        }
    return {
        "message": f"Đã crawl {len(result['logs'])} nguồn active",
        "results": result["logs"],
        "skipped": False,
    }


@router.post("/trigger/{source_id}", dependencies=[Depends(require_api_key)])
async def trigger_one_crawl(source_id: str) -> dict:
    try:
        result = await crawl_one_source(source_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Lỗi crawl: {error}") from error

    return {"message": "Đã crawl nguồn thành công", "result": result}


@router.post("/preview", dependencies=[Depends(require_api_key)])
async def crawl_preview(payload: CrawlPreviewRequest) -> dict:
    html = await fetch_html(str(payload.url))
    # Parse HTML một lần thay vì truyền raw string vào mỗi extract call —
    # tiết kiệm 4x chi phí build BS4 tree.
    soup = parse_html(html)
    sel = payload.selectors
    stype = payload.selector_type

    title = extract_text(soup, sel.title, stype)
    author = extract_text(soup, sel.author, stype)
    content = extract_text(soup, sel.content, stype)
    published_at_raw = extract_text(soup, sel.published_at, stype)
    image_url = extract_attribute(soup, sel.image, "content", stype) or extract_attribute(
        soup, sel.image, "src", stype
    )

    if content:
        content = content[:200]

    return {
        "title": title,
        "author": author,
        "content": content,
        "published_at": published_at_raw or datetime.now(UTC).isoformat(),
        "image_url": image_url,
    }
