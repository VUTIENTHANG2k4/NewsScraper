import httpx
from playwright.async_api import async_playwright

from config import settings

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


def make_http_client() -> httpx.AsyncClient:
    """Tạo AsyncClient để reuse cho toàn bộ session crawl của 1 nguồn."""
    return httpx.AsyncClient(
        timeout=settings.http_timeout_seconds,
        follow_redirects=True,
        trust_env=True,
        headers=DEFAULT_HEADERS,
    )


async def fetch_html(
    url: str,
    client: httpx.AsyncClient | None = None,
    timeout: float | None = None,
) -> str:
    """Fetch HTML qua HTTP. Nếu truyền client thì tái sử dụng kết nối (nhanh hơn)."""
    if client is not None:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
    async with httpx.AsyncClient(
        timeout=timeout if timeout is not None else settings.http_timeout_seconds,
        follow_redirects=True,
        trust_env=True,
        headers=DEFAULT_HEADERS,
    ) as c:
        response = await c.get(url)
        response.raise_for_status()
        return response.text


async def fetch_html_playwright_batch(
    urls: list[str], timeout: float | None = None
) -> dict[str, "str | Exception"]:
    """
    Fetch nhiều URL với MỘT browser instance duy nhất.
    Thay vì launch N browser, chỉ launch 1 lần → tiết kiệm ~2-3s/bài.
    """
    if not urls:
        return {}

    results: dict[str, str | Exception] = {}
    timeout_seconds = timeout if timeout is not None else settings.playwright_timeout_seconds
    timeout_ms = int(timeout_seconds * 1000)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            context = await browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"])
            for url in urls:
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                    await page.wait_for_timeout(1000)
                    results[url] = await page.content()
                except Exception as exc:  # noqa: BLE001
                    results[url] = exc
                finally:
                    await page.close()
        finally:
            await browser.close()

    return results
