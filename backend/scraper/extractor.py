from urllib.parse import urlparse

from bs4 import BeautifulSoup


def _is_xpath(selector: str, selector_type: str) -> bool:
    return selector_type.lower() == "xpath" or selector.strip().startswith("/")


def extract_text(html: str, selector: str, selector_type: str = "css") -> str | None:
    if not selector:
        return None
    soup = BeautifulSoup(html, "lxml")
    if _is_xpath(selector, selector_type):
        # Sprint 1 ưu tiên CSS, XPath sẽ mở rộng ở Sprint sau.
        return None

    element = soup.select_one(selector)
    if element is None:
        return None
    return element.get_text(" ", strip=True) or None


def extract_attribute(
    html: str,
    selector: str,
    attribute: str,
    selector_type: str = "css",
) -> str | None:
    if not selector:
        return None
    soup = BeautifulSoup(html, "lxml")
    if _is_xpath(selector, selector_type):
        return None

    element = soup.select_one(selector)
    if element is None:
        return None

    value = element.get(attribute)
    if value:
        return str(value).strip()
    return None


def extract_article_links(
    html: str,
    selector: str,
    base_url: str,
    selector_type: str = "css",
) -> list[str]:
    if not selector:
        return []

    soup = BeautifulSoup(html, "lxml")
    if _is_xpath(selector, selector_type):
        return []

    links: list[str] = []
    for anchor in soup.select(selector):
        href = anchor.get("href")
        if not href:
            continue
        href = href.strip()
        if href.startswith("//"):
            links.append(f"https:{href}")
            continue
        if href.startswith("/"):
            links.append(base_url.rstrip("/") + href)
            continue
        if href.startswith("http://") or href.startswith("https://"):
            links.append(href)

    # Giữ thứ tự và loại trùng.
    unique_links = list(dict.fromkeys(links))
    return unique_links


def extract_same_domain_article_links(
    html: str, base_url: str, max_links: int = 20
) -> list[str]:
    """
    Dự phòng khi chưa cấu hình article_list: thu thập link cùng domain từ trang chủ.
    Dùng cùng ý tưởng với scripts/run_sprint1_crawl_proof.py.
    """
    try:
        domain = urlparse(base_url).netloc
    except ValueError:
        return []

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
        if href.rstrip("/") == base_url.rstrip("/"):
            continue
        if any(
            token in href.lower()
            for token in [
                "javascript:",
                "/video",
                "/photo",
                "/tag/",
                "/tim-kiem",
                "/search",
            ]
        ):
            continue
        links.append(href)

    unique = list(dict.fromkeys(links))
    return unique[: max_links] if max_links else unique


def extract_fallback_title(html: str) -> str | None:
    """Khi chưa có CSS title: ưu tiên og:title, rồi h1, rồi <title>."""
    soup = BeautifulSoup(html, "lxml")
    og = soup.select_one('meta[property="og:title"]')
    if og and (og.get("content") or "").strip():
        return (og.get("content") or "").strip()
    tw = soup.select_one('meta[name="twitter:title"]')
    if tw and (tw.get("content") or "").strip():
        return (tw.get("content") or "").strip()
    h1 = soup.select_one("h1")
    if h1:
        t = h1.get_text(" ", strip=True)
        if t:
            return t
    title = soup.find("title")
    if title:
        t = title.get_text(" ", strip=True)
        if t:
            return t
    return None


def extract_fallback_text_content(html: str) -> str | None:
    """Khi chưa có CSS nội dung: ưu tiên article/main rồi tới toàn bộ body."""
    soup = BeautifulSoup(html, "lxml")
    for sel in (
        "article",
        "main",
        '[role="main"]',
        ".article__body",
        ".content-detail",
        ".detail-content",
    ):
        el = soup.select_one(sel)
        if el:
            t = el.get_text(" ", strip=True)
            if t and len(t) > 80:
                return t
    body = soup.find("body")
    if body:
        t = body.get_text(" ", strip=True)
        return t if t else None
    return None


def extract_fallback_og_image(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    meta = soup.select_one('meta[property="og:image"]') or soup.select_one(
        'meta[name="twitter:image"]'
    )
    if meta and (meta.get("content") or "").strip():
        return (meta.get("content") or "").strip()
    return None
