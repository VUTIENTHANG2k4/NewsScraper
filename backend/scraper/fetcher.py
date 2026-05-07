import httpx
from playwright.async_api import async_playwright

HTTP_TIMEOUT_SECONDS = 30.0
PLAYWRIGHT_TIMEOUT_SECONDS = 60.0

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


async def fetch_html(url: str, timeout: float = HTTP_TIMEOUT_SECONDS) -> str:
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, trust_env=True
    ) as client:
        response = await client.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response.text


async def fetch_html_playwright(
    url: str, timeout: float = PLAYWRIGHT_TIMEOUT_SECONDS
) -> str:
    timeout_ms = int(timeout * 1000)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            context = await browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"])
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            await page.wait_for_timeout(1000)
            return await page.content()
        finally:
            await browser.close()


async def fetch_html_by_crawl_type(crawl_type: str, url: str) -> str:
    if crawl_type == "playwright":
        return await fetch_html_playwright(url)
    return await fetch_html(url)
