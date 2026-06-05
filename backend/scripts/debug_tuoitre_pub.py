"""Debug published_at extraction cho 1 bài Tuoi Tre."""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scraper.extractor import (
    extract_fallback_published_at,
    extract_text,
    parse_html,
)
from scraper.fetcher import fetch_html


async def main() -> None:
    url = "https://tuoitre.vn/tong-bi-thu-chu-tich-nuoc-to-lam-va-nhieu-lanh-dao-du-dai-hoi-xiv-cong-doan-viet-nam-20260604082441438.htm"
    html = await fetch_html(url)
    soup = parse_html(html)

    print("primary `.date-time`:", repr(extract_text(soup, ".date-time")))
    print("fallback meta:", repr(extract_fallback_published_at(soup)))
    print()
    print("Candidates trong HTML:")
    candidates = [
        'meta[property="article:published_time"]',
        'meta[itemprop="datePublished"]',
        'meta[name="pubdate"]',
        'meta[name="publishdate"]',
        "time[datetime]",
        '[data-role="publishdate"]',
        ".detail-time",
        ".date-publish",
    ]
    for sel in candidates:
        el = soup.select_one(sel)
        if el is None:
            print(f"  {sel:50s} → NOT FOUND")
        else:
            attrs = dict(el.attrs)
            text = el.get_text(" ", strip=True)[:80]
            print(f"  {sel:50s} → attrs={attrs}, text={text!r}")


if __name__ == "__main__":
    asyncio.run(main())
