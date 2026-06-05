import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from bson import ObjectId
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from config import settings
from db.lock import try_acquire
from db.mongo import get_collections
from models.news import NewsItemCreate
from scraper.extractor import (
    extract_article_links,
    extract_attribute,
    extract_fallback_og_image,
    extract_fallback_published_at,
    extract_fallback_text_content,
    extract_fallback_title,
    extract_same_domain_article_links,
    extract_text,
    parse_html,
)
from scraper.fetcher import (
    fetch_html,
    fetch_html_playwright_batch,
    make_http_client,
)
from scraper.normalizer import clean_text, try_parse_datetime

logger = logging.getLogger(__name__)

# Giới hạn số nguồn crawl đồng thời để không tranh chấp CPU với request API.
_CRAWL_SEMAPHORE = asyncio.Semaphore(settings.crawl_concurrency)


def _extract_article_data(soup, selectors: dict, selector_type: str) -> dict:
    """Trích xuất toàn bộ field bài viết từ soup đã parse — không parse lại HTML."""
    title = clean_text(
        extract_text(soup, selectors.get("title", ""), selector_type)
    ) or clean_text(extract_fallback_title(soup))

    author = clean_text(
        extract_text(soup, selectors.get("author", ""), selector_type),
        max_length=250,
    )

    content = clean_text(
        extract_text(soup, selectors.get("content", ""), selector_type),
        max_length=settings.content_max_length,
    ) or clean_text(
        extract_fallback_text_content(soup),
        max_length=settings.content_max_length,
    )

    # Ưu tiên selector site-specific. Nếu parse được thì OK; nếu lấy được string
    # nhưng parse fail (tiếng Việt, format lạ…) → thử lại với meta tag chuẩn
    # schema.org. Tránh việc âm thầm fallback về now() khiến published_at vô nghĩa.
    primary_raw = extract_text(soup, selectors.get("published_at", ""), selector_type)
    fallback_raw = None  # sẽ lazy-load nếu primary parse fail

    image_url = (
        extract_attribute(soup, selectors.get("image", ""), "content", selector_type)
        or extract_attribute(soup, selectors.get("image", ""), "src", selector_type)
        or extract_fallback_og_image(soup)
    )

    date_format = selectors.get("date_format") or None
    published_at = try_parse_datetime(primary_raw, date_format)
    if published_at is None:
        fallback_raw = extract_fallback_published_at(soup)
        published_at = try_parse_datetime(fallback_raw)
    if published_at is None:
        published_at = datetime.now(UTC)

    return {
        "title": title,
        "author": author,
        "content": content,
        "published_at": published_at,
        "image_url": image_url,
    }


def _build_news_document(
    article_url: str,
    soup,
    selectors: dict,
    selector_type: str,
    source_id: str,
    source_name: str,
) -> dict | None:
    """Build news document, trả None nếu thiếu cả title lẫn content."""
    data = _extract_article_data(soup, selectors, selector_type)

    if not data["title"] and not data["content"]:
        return None

    candidate = {
        "source_id": source_id,
        "source_name": source_name,
        "source_url": article_url,
        "title": data["title"],
        "author": data["author"],
        "content": data["content"],
        "image_url": data["image_url"],
        "published_at": data["published_at"],
        "created_at": datetime.now(UTC),
    }

    # Validate qua pydantic model — bắt sớm dữ liệu không hợp lệ trước khi insert.
    try:
        NewsItemCreate.model_validate(candidate)
    except ValidationError as exc:
        logger.warning("Bỏ qua bài (validate fail) %s: %s", article_url, exc)
        return None

    return candidate


async def _process_articles(
    article_links: list[str],
    fetch_one: Callable[[str], Awaitable[str]],
    selectors: dict,
    selector_type: str,
    source_id: str,
    source_name: str,
) -> tuple[list[dict], str]:
    """
    Xử lý danh sách bài bằng callable fetch chung — tránh trùng lặp giữa
    HTTP và Playwright.
    """
    documents: list[dict] = []
    status = "success"

    for article_url in article_links:
        try:
            article_html = await fetch_one(article_url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fetch article failed for %s: %s", article_url, exc)
            status = "partial"
            continue

        soup = parse_html(article_html)
        document = _build_news_document(
            article_url, soup, selectors, selector_type, source_id, source_name
        )
        if document is None:
            logger.warning(
                "Bỏ qua bài (không có title/content hoặc invalid): %s", article_url
            )
            status = "partial"
            continue

        documents.append(document)

    return documents, status


async def _crawl_source(source: dict) -> dict:
    collections = get_collections()
    selectors = source.get("selectors", {})
    selector_type = source.get("selector_type", "css")
    crawl_type = source.get("crawl_type", "http")
    source_id = str(source["_id"])
    source_name = source["name"]
    base_url = source["base_url"]

    crawled_at = datetime.now(UTC)
    articles_new = 0
    articles_found = 0
    status = "success"
    error_msg = None

    try:
        if crawl_type == "playwright":
            # Dùng MỘT browser cho cả homepage + articles → tiết kiệm ~2-3s
            # so với launch 2 lần. Có retry cho homepage để chống lỗi mạng tạm thời.
            homepage_html = await _fetch_html_playwright_with_retry(base_url)

            homepage_soup = parse_html(homepage_html)
            article_links = _extract_links(homepage_soup, base_url, selectors, selector_type)
            articles_found = len(article_links)

            article_html_map = await fetch_html_playwright_batch(article_links)

            async def fetch_one(url: str) -> str:
                result = article_html_map.get(url)
                if isinstance(result, Exception) or result is None:
                    raise result or RuntimeError("Không có HTML cho bài")
                return result

            documents, status = await _process_articles(
                article_links, fetch_one, selectors, selector_type, source_id, source_name
            )
        else:
            async with make_http_client() as http_client:
                homepage_html = await _fetch_html_with_retry(base_url, client=http_client)
                homepage_soup = parse_html(homepage_html)
                article_links = _extract_links(
                    homepage_soup, base_url, selectors, selector_type
                )
                articles_found = len(article_links)

                async def fetch_one(url: str, _c=http_client) -> str:
                    return await _fetch_html_with_retry(url, client=_c)

                documents, status = await _process_articles(
                    article_links, fetch_one, selectors, selector_type, source_id, source_name
                )

        for document in documents:
            try:
                await collections["news"].insert_one(document)
                articles_new += 1
            except DuplicateKeyError:
                continue
            except Exception as insert_error:  # noqa: BLE001
                logger.warning(
                    "Insert article failed for %s: %s",
                    document.get("source_url"),
                    insert_error,
                )
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
    crawl_log.pop("_id", None)
    return crawl_log


def _extract_links(soup, base_url: str, selectors: dict, selector_type: str) -> list[str]:
    list_selector = (selectors.get("article_list", "") or "").strip()
    if list_selector:
        return extract_article_links(
            soup, list_selector, base_url=base_url, selector_type=selector_type
        )
    return extract_same_domain_article_links(
        soup, base_url, max_links=settings.max_links_per_source
    )


async def _retry_with_backoff(
    fetch_fn: Callable[[], Awaitable[str]], url: str
) -> str:
    """Wrapper retry với exponential backoff dùng chung cho HTTP và Playwright."""
    last_error: Exception | None = None
    attempts = max(1, settings.http_retry_count + 1)
    for attempt in range(attempts):
        try:
            return await fetch_fn()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt + 1 >= attempts:
                break
            backoff = settings.http_retry_backoff_seconds * (2**attempt)
            logger.info(
                "Retry %d/%d sau %.1fs cho %s (%s)",
                attempt + 1,
                attempts - 1,
                backoff,
                url,
                exc,
            )
            await asyncio.sleep(backoff)
    assert last_error is not None
    raise last_error


async def _fetch_html_with_retry(url: str, client=None) -> str:
    return await _retry_with_backoff(lambda: fetch_html(url, client=client), url)


async def _fetch_html_playwright_with_retry(url: str) -> str:
    async def _once() -> str:
        result_map = await fetch_html_playwright_batch([url])
        result = result_map.get(url)
        if isinstance(result, Exception):
            raise result
        if result is None:
            raise RuntimeError("Không lấy được HTML từ Playwright")
        return result

    return await _retry_with_backoff(_once, url)


async def crawl_one_source(source_id: str) -> dict:
    """
    Crawl một nguồn cụ thể. Dùng lock per-source để tránh chạy đồng thời
    với scheduled crawl hoặc manual trigger khác cho cùng nguồn đó.
    """
    collections = get_collections()
    source = await collections["sources"].find_one({"_id": ObjectId(source_id)})
    if source is None:
        raise ValueError("Nguon khong ton tai")

    lock_name = f"crawl_source_{source_id}"
    async with try_acquire(lock_name, ttl_seconds=600) as acquired:
        if not acquired:
            raise RuntimeError("Nguồn này đang được crawl bởi tiến trình khác.")
        return await _crawl_source(source)


async def _crawl_source_with_limit(source: dict) -> dict:
    async with _CRAWL_SEMAPHORE:
        return await _crawl_source(source)


async def crawl_active_sources() -> dict:
    """
    Chạy crawl cho mọi nguồn active. Dùng distributed lock trên Mongo để
    nhiều instance backend chạy song song chỉ có 1 instance thực sự crawl
    mỗi mốc lập lịch — tránh tốn tài nguyên trùng lặp khi scale ngang.

    Returns:
        dict với key:
        - acquired (bool): có chiếm được lock không
        - logs (list[dict]): kết quả crawl từng nguồn (rỗng nếu skipped)
        - skipped_reason (str | None): lý do nếu không crawl
    """
    async with try_acquire(
        "crawl_active_sources", ttl_seconds=settings.crawl_lock_ttl_seconds
    ) as acquired:
        if not acquired:
            logger.info("Bỏ qua run: instance khác đang giữ lock crawl_active_sources.")
            return {
                "acquired": False,
                "logs": [],
                "skipped_reason": "Instance khác đang chạy crawl.",
            }

        collections = get_collections()
        sources = (
            await collections["sources"].find({"is_active": True}).to_list(length=None)
        )
        if not sources:
            return {
                "acquired": True,
                "logs": [],
                "skipped_reason": "Không có nguồn active.",
            }

        tasks = [_crawl_source_with_limit(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        crawl_logs: list[dict] = []
        for source, result in zip(sources, results, strict=False):
            if isinstance(result, Exception):
                logger.exception(
                    "Unhandled crawl error for %s",
                    source.get("name"),
                    exc_info=result,
                )
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
                fallback_log.pop("_id", None)
                crawl_logs.append(fallback_log)
                continue
            crawl_logs.append(result)

        return {"acquired": True, "logs": crawl_logs, "skipped_reason": None}
