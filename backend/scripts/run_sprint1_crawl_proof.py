import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scraper.fetcher import fetch_html

REPORT_JSON_PATH = Path(__file__).resolve().parents[2] / "reports" / "sprint1_crawl5_report.json"
REPORT_MD_PATH = Path(__file__).resolve().parents[2] / "reports" / "sprint1_crawl5_report.md"

TARGET_SOURCES = [
    {"name": "VnExpress", "base_url": "https://vnexpress.net"},
    {"name": "Tuoi Tre", "base_url": "https://tuoitre.vn"},
    {"name": "Thanh Nien", "base_url": "https://thanhnien.vn"},
    {"name": "Dan Tri", "base_url": "https://dantri.com.vn"},
    {"name": "Zing News", "base_url": "https://zingnews.vn"},
]


def extract_same_domain_article_links(html: str, base_url: str, max_links: int = 10) -> list[str]:
    domain = urlparse(base_url).netloc
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []

    for anchor in soup.select("a[href]"):
        href = (anchor.get("href") or "").strip()
        if not href:
            continue
        if href.startswith("//"):
            href = f"https:{href}"
        elif href.startswith("/"):
            href = base_url.rstrip("/") + href
        if not href.startswith("http://") and not href.startswith("https://"):
            continue
        parsed = urlparse(href)
        if parsed.netloc != domain:
            continue
        # Loại bỏ link không giống bài viết.
        if any(
            token in href.lower()
            for token in ["javascript:", "/video", "/photo", "/tag/", "/tim-kiem", "/search"]
        ):
            continue
        links.append(href)

    unique_links = list(dict.fromkeys(links))
    return unique_links[:max_links]


def extract_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("title")
    if title is None:
        return None
    text = title.get_text(strip=True)
    return text or None


async def crawl_source_once(source: dict) -> dict:
    started_at = time.perf_counter()
    source_result: dict = {
        "source_name": source["name"],
        "base_url": source["base_url"],
        "status": "success",
        "error": None,
        "homepage_fetch_ms": 0,
        "article_links_found": 0,
        "article_links_sample": [],
        "article_fetch_attempted": 0,
        "article_fetch_succeeded": 0,
        "article_titles_sample": [],
    }
    try:
        homepage_start = time.perf_counter()
        homepage_html = await fetch_html(source["base_url"], timeout=30.0)
        source_result["homepage_fetch_ms"] = round((time.perf_counter() - homepage_start) * 1000, 2)

        article_links = extract_same_domain_article_links(homepage_html, source["base_url"], max_links=10)
        source_result["article_links_found"] = len(article_links)
        source_result["article_links_sample"] = article_links[:5]

        for article_url in article_links[:3]:
            source_result["article_fetch_attempted"] += 1
            try:
                article_html = await fetch_html(article_url, timeout=30.0)
                source_result["article_fetch_succeeded"] += 1
                title = extract_title(article_html)
                if title:
                    source_result["article_titles_sample"].append(title)
            except Exception as article_error:  # noqa: BLE001
                source_result["status"] = "partial"
                source_result["error"] = f"Article fetch issue: {article_error}"
    except Exception as source_error:  # noqa: BLE001
        source_result["status"] = "error"
        source_result["error"] = str(source_error)

    source_result["total_elapsed_ms"] = round((time.perf_counter() - started_at) * 1000, 2)
    return source_result


def build_markdown_report(report: dict) -> str:
    lines = []
    lines.append("# Sprint 1 Crawl Proof (5 HTTP sources)")
    lines.append("")
    lines.append(f"- Run at (UTC): `{report['run_at_utc']}`")
    lines.append(f"- Total sources tested: `{report['total_sources']}`")
    lines.append(f"- Success count: `{report['success_count']}`")
    lines.append(f"- Partial count: `{report['partial_count']}`")
    lines.append(f"- Error count: `{report['error_count']}`")
    lines.append(f"- Total elapsed: `{report['total_elapsed_ms']} ms`")
    lines.append("")
    lines.append("## Source Results")
    lines.append("")
    for item in report["results"]:
        lines.append(f"### {item['source_name']}")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Homepage fetch: `{item['homepage_fetch_ms']} ms`")
        lines.append(f"- Article links found: `{item['article_links_found']}`")
        lines.append(
            f"- Article fetch success: `{item['article_fetch_succeeded']}/{item['article_fetch_attempted']}`"
        )
        if item["article_titles_sample"]:
            lines.append("- Sample titles:")
            for title in item["article_titles_sample"][:3]:
                lines.append(f"  - {title}")
        if item["error"]:
            lines.append(f"- Error: `{item['error']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


async def main() -> None:
    run_started = time.perf_counter()
    results = await asyncio.gather(*(crawl_source_once(source) for source in TARGET_SOURCES))

    success_count = sum(1 for item in results if item["status"] == "success")
    partial_count = sum(1 for item in results if item["status"] == "partial")
    error_count = sum(1 for item in results if item["status"] == "error")

    report = {
        "run_at_utc": datetime.now(UTC).isoformat(),
        "total_sources": len(TARGET_SOURCES),
        "success_count": success_count,
        "partial_count": partial_count,
        "error_count": error_count,
        "total_elapsed_ms": round((time.perf_counter() - run_started) * 1000, 2),
        "results": results,
    }

    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD_PATH.write_text(build_markdown_report(report), encoding="utf-8")

    print(f"Report JSON: {REPORT_JSON_PATH}")
    print(f"Report MD: {REPORT_MD_PATH}")
    print(
        "Summary:",
        f"success={success_count}, partial={partial_count}, error={error_count},",
        f"elapsed={report['total_elapsed_ms']}ms",
    )


if __name__ == "__main__":
    asyncio.run(main())
