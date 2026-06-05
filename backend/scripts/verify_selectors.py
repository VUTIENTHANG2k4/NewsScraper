"""
Script kiểm tra selectors mặc định cho 4 nguồn lớn (VnExpress / Tuoi Tre / Thanh Nien / Dan Tri).

Cách dùng (trong container backend):
    docker compose exec backend python scripts/verify_selectors.py

Quy trình mỗi nguồn:
  1. Fetch homepage qua HTTP, áp dụng selector `article_list` để lấy link bài.
  2. Fetch 1 link bài đầu tiên, áp dụng selectors cho title/content/published_at/image.
  3. In ra terminal: số link tìm được + có lấy được từng field hay không.

Mục tiêu: phát hiện sớm các selector bị sai do site đổi class HTML, trước khi
quyết định PATCH selector cho các source trong DB.
"""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scraper.extractor import (
    extract_article_links,
    extract_attribute,
    extract_fallback_published_at,
    extract_fallback_text_content,
    extract_fallback_title,
    extract_text,
    parse_html,
)
from scraper.fetcher import fetch_html
from scraper.normalizer import normalize_datetime

CASES = [
    {
        "name": "VnExpress",
        "base_url": "https://vnexpress.net",
        "selectors": {
            "article_list": "h3.title-news a, h2.title-news a",
            "title": "h1.title-detail",
            "author": ".author",
            "content": "article.fck_detail",
            "published_at": ".date",
            "image": 'meta[property="og:image"]',
        },
    },
    {
        "name": "Tuoi Tre",
        "base_url": "https://tuoitre.vn",
        "selectors": {
            "article_list": "h3.box-title-news a, a.box-category-link-title",
            "title": "h1.article-title, h1.detail-title",
            "author": ".author-info",
            "content": ".detail-content",
            "published_at": ".date-time",
            "image": 'meta[property="og:image"]',
        },
    },
    {
        "name": "Thanh Nien",
        "base_url": "https://thanhnien.vn",
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
        },
    },
    {
        "name": "Dan Tri",
        "base_url": "https://dantri.com.vn",
        "selectors": {
            "article_list": "h3.article-title a, h2.article-title a",
            "title": "h1.title-page, h1.singular-title",
            "author": ".author-name",
            "content": ".singular-content, .dt-news__content",
            "published_at": ".author-time, time",
            "image": 'meta[property="og:image"]',
        },
    },
]


def status_label(value: str | None, *, ok_min_len: int = 1) -> str:
    if value and len(str(value).strip()) >= ok_min_len:
        return "OK"
    return "MISS"


async def verify_one(case: dict) -> dict:
    name = case["name"]
    base_url = case["base_url"]
    sel = case["selectors"]

    out: dict = {
        "name": name,
        "homepage_ok": False,
        "links_found": 0,
        "first_article": None,
        "fields": {},
    }

    try:
        homepage_html = await fetch_html(base_url)
        out["homepage_ok"] = True
    except Exception as exc:
        out["error"] = f"fetch homepage: {exc}"
        return out

    soup = parse_html(homepage_html)
    links = extract_article_links(soup, sel["article_list"], base_url=base_url)
    out["links_found"] = len(links)
    if not links:
        return out

    article_url = links[0]
    out["first_article"] = article_url
    try:
        article_html = await fetch_html(article_url)
    except Exception as exc:
        out["error"] = f"fetch article: {exc}"
        return out

    asoup = parse_html(article_html)

    title = extract_text(asoup, sel["title"]) or extract_fallback_title(asoup)
    author = extract_text(asoup, sel["author"]) if sel["author"] else None
    content = extract_text(asoup, sel["content"]) or extract_fallback_text_content(asoup)
    published_raw = extract_text(asoup, sel["published_at"]) or extract_fallback_published_at(
        asoup
    )
    published = (
        normalize_datetime(published_raw, None).isoformat() if published_raw else None
    )
    image_url = (
        extract_attribute(asoup, sel["image"], "content")
        or extract_attribute(asoup, sel["image"], "src")
    )

    out["fields"] = {
        "title": (status_label(title), (title or "")[:60]),
        "author": (status_label(author), (author or "")[:40]) if sel["author"] else ("SKIP", "—"),
        "content": (status_label(content, ok_min_len=80), f"len={len(content or '')}"),
        "published_raw": (status_label(published_raw), (published_raw or "")[:40]),
        "published_parsed": (status_label(published), (published or "")[:30]),
        "image": (status_label(image_url), (image_url or "")[:60]),
    }
    return out


async def main() -> None:
    print("=" * 78)
    print("Selector verification report")
    print("=" * 78)

    results = await asyncio.gather(*(verify_one(case) for case in CASES))

    for r in results:
        print(f"\n[{r['name']}] base_url={CASES[results.index(r)]['base_url']}")
        if not r["homepage_ok"]:
            print(f"  homepage: FAIL ({r.get('error')})")
            continue
        print(f"  homepage: OK | article_list found {r['links_found']} link(s)")
        if not r["links_found"]:
            print("  → article_list selector cần xem lại")
            continue
        print(f"  first article: {r['first_article']}")
        if "error" in r:
            print(f"  fetch article: FAIL ({r['error']})")
            continue
        for field, (label, sample) in r["fields"].items():
            print(f"  {field:18s} [{label:4s}] {sample}")

    print("\n" + "=" * 78)
    misses = sum(
        1
        for r in results
        for label, _ in r.get("fields", {}).values()
        if label == "MISS"
    )
    print(f"Total MISS fields across 4 sources: {misses}")
    print("=" * 78)


if __name__ == "__main__":
    asyncio.run(main())
