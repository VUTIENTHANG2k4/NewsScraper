import asyncio
import logging
from datetime import UTC, datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from db.mongo import get_collections
from scraper.extractor import (
    extract_article_links,
    extract_attribute,
    extract_fallback_og_image,
    extract_fallback_text_content,
    extract_fallback_title,
    extract_same_domain_article_links,
    extract_text,
)
from scraper.fetcher import fetch_html_by_crawl_type
from scraper.normalizer import clean_text, is_duplicate_source_url, normalize_datetime

logger = logging.getLogger(__name__)


async def _crawl_source(source: dict) -> dict:
    collections = get_collections()
    selectors = source.get("selectors", {})
    selector_type = source.get("selector_type", "css")
    crawl_type = source.get("crawl_type", "http")
    source_id = str(source["_id"])
    source_name = source["name"]
    base_url = source["base_url"]

    crawled_at = datetime.now(UTC)
    articles_found = 0
    articles_new = 0
    status = "success"
    error_msg = None

    try:
        homepage_html = await fetch_html_by_crawl_type(crawl_type, base_url)
        list_selector = selectors.get("article_list", "") or ""
        if list_selector.strip():
            article_links = extract_article_links(
                homepage_html,
                list_selector,
                base_url=base_url,
                selector_type=selector_type,
            )
        else:
            # Nguồn seed mặc định chưa có CSS: dùng heuristic cùng domain
            # (Sprint 1 — phần điền selector thủ công tùy trang).
            article_links = extract_same_domain_article_links(
                homepage_html, base_url, max_links=20
            )
        articles_found = len(article_links)

        for article_url in article_links:
            try:
                article_html = await fetch_html_by_crawl_type(crawl_type, article_url)
            except Exception as article_error:  # noqa: BLE001
                logger.warning("Fetch article failed for %s: %s", article_url, article_error)
                status = "partial"
                continue

            title = clean_text(
                extract_text(article_html, selectors.get("title", ""), selector_type)
            ) or clean_text(extract_fallback_title(article_html))
            author = clean_text(
                extract_text(article_html, selectors.get("author", ""), selector_type),
                max_length=250,
            )
            content = clean_text(
                extract_text(article_html, selectors.get("content", ""), selector_type),
            ) or clean_text(extract_fallback_text_content(article_html))
            published_raw = extract_text(
                article_html,
                selectors.get("published_at", ""),
                selector_type,
            )
            image_url = extract_attribute(
                article_html,
                selectors.get("image", ""),
                "content",
                selector_type,
            ) or extract_attribute(
                article_html,
                selectors.get("image", ""),
                "src",
                selector_type,
            ) or extract_fallback_og_image(article_html)

            if not title and not content:
                logger.warning("Bo qua bai (khong lay duoc title/content): %s", article_url)
                status = "partial"
                continue

            document = {
                "source_id": source_id,
                "source_name": source_name,
                "source_url": article_url,
                "title": title,
                "author": author,
                "content": content,
                "image_url": image_url,
                "published_at": normalize_datetime(
                    published_raw, selectors.get("date_format")
                ),
                "created_at": datetime.now(UTC),
            }

            try:
                if await is_duplicate_source_url(collections["news"], article_url):
                    continue
            except Exception as dedup_error:  # noqa: BLE001
                logger.warning("Dedup check failed for %s: %s", article_url, dedup_error)
                status = "partial"

            try:
                await collections["news"].insert_one(document)
                articles_new += 1
            except DuplicateKeyError:
                continue
            except Exception as insert_error:  # noqa: BLE001
                logger.warning("Insert article failed for %s: %s", article_url, insert_error)
                status = "partial"

        await collections["sources"].update_one(
            {"_id": source["_id"]},
            {"$set": {"last_crawled": datetime.now(UTC)}},
        )

    except Exception as source_error:  # noqa: BLE001
        status = "error"
        error_msg = str(source_error)
        logger.exception("Crawl source failed: %s", source_name)

    crawl_log = {
        "source_id": source_id,
        "source_name": source_name,
        "crawled_at": crawled_at,
        "articles_found": articles_found,
        "articles_new": articles_new,
        "status": status,
        "error_msg": error_msg,
    }
    await collections["crawl_logs"].insert_one(crawl_log)
    return crawl_log


async def crawl_one_source(source_id: str) -> dict:
    collections = get_collections()
    source = await collections["sources"].find_one({"_id": ObjectId(source_id)})
    if source is None:
        raise ValueError("Nguon khong ton tai")
    return await _crawl_source(source)


async def crawl_active_sources() -> list[dict]:
    collections = get_collections()
    sources = await collections["sources"].find({"is_active": True}).to_list(length=None)
    if not sources:
        return []
    tasks = [_crawl_source(source) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    crawl_logs: list[dict] = []
    for source, result in zip(sources, results, strict=False):
        if isinstance(result, Exception):
            logger.exception("Unhandled crawl error for %s", source.get("name"), exc_info=result)
            fallback_log = {
                "source_id": str(source["_id"]),
                "source_name": source.get("name"),
                "crawled_at": datetime.now(UTC),
                "articles_found": 0,
                "articles_new": 0,
                "status": "error",
                "error_msg": str(result),
            }
            await collections["crawl_logs"].insert_one(fallback_log)
            crawl_logs.append(fallback_log)
            continue
        crawl_logs.append(result)

    return crawl_logs
