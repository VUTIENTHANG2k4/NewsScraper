from datetime import UTC, datetime

from db.mongo import get_collections


def _empty_selectors() -> dict:
    return {
        "article_list": "",
        "title": "",
        "author": "",
        "content": "",
        "published_at": "",
        "image": "",
        "date_format": "",
    }


def _selectors(**overrides) -> dict:
    base = _empty_selectors()
    base.update(overrides)
    return base


# Một số nguồn lớn: cấu hình selector tối thiểu để lấy được title/content/published_at
# chính xác thay vì rơi vào fallback (vốn gán published_at = now()).
SEED_SOURCES = [
    {
        "name": "VnExpress",
        "base_url": "https://vnexpress.net",
        "crawl_type": "http",
        "selectors": _selectors(
            article_list="h3.title-news a, h2.title-news a",
            title="h1.title-detail",
            author=".author",
            content="article.fck_detail",
            published_at=".date",
            image='meta[property="og:image"]',
        ),
    },
    {
        "name": "Tuoi Tre",
        "base_url": "https://tuoitre.vn",
        "crawl_type": "http",
        "selectors": _selectors(
            article_list="h3.box-title-news a, a.box-category-link-title",
            title="h1.article-title, h1.detail-title",
            author=".author-info",
            content=".detail-content",
            published_at=".date-time",
            image='meta[property="og:image"]',
        ),
    },
    {
        "name": "Thanh Nien",
        "base_url": "https://thanhnien.vn",
        "crawl_type": "http",
        "selectors": _selectors(
            article_list=(
                "h2.box-title-text a, h3.box-title-text a, "
                "h2.story__title a, h3.story__title a, "
                ".box-category-item a.box-category-link-title"
            ),
            title="h1.detail-title, h1.story__title",
            content=".detail-content, .story__detail",
            image='meta[property="og:image"]',
        ),
    },
    {
        "name": "Dan Tri",
        "base_url": "https://dantri.com.vn",
        "crawl_type": "http",
        "selectors": _selectors(
            article_list="h3.article-title a, h2.article-title a",
            title="h1.title-page, h1.singular-title",
            author=".author-name",
            content=".singular-content, .dt-news__content",
            published_at=".author-time, time",
            image='meta[property="og:image"]',
        ),
    },
    {"name": "Zing News", "base_url": "https://zingnews.vn", "crawl_type": "http"},
    {"name": "VietnamNet", "base_url": "https://vietnamnet.vn", "crawl_type": "http"},
    {"name": "Nhan Dan", "base_url": "https://nhandan.vn", "crawl_type": "http"},
    {"name": "Lao Dong", "base_url": "https://laodong.vn", "crawl_type": "http"},
    {"name": "Tien Phong", "base_url": "https://tienphong.vn", "crawl_type": "http"},
    {"name": "Nguoi Lao Dong", "base_url": "https://nld.com.vn", "crawl_type": "http"},
    {"name": "Phap Luat TP.HCM", "base_url": "https://plo.vn", "crawl_type": "http"},
    {"name": "An Ninh Thu Do", "base_url": "https://anninhthudo.vn", "crawl_type": "http"},
    {
        "name": "Suc Khoe Doi Song",
        "base_url": "https://suckhoedoisong.vn",
        "crawl_type": "http",
    },
    {"name": "CafeF", "base_url": "https://cafef.vn", "crawl_type": "http"},
    {"name": "VnEconomy", "base_url": "https://vneconomy.vn", "crawl_type": "http"},
    {"name": "ICTNews", "base_url": "https://ictnews.vn", "crawl_type": "http"},
    {"name": "Bao Moi", "base_url": "https://baomoi.com", "crawl_type": "playwright"},
    {"name": "Kenh14", "base_url": "https://kenh14.vn", "crawl_type": "playwright"},
    {"name": "GameK", "base_url": "https://gamek.vn", "crawl_type": "http"},
    {
        "name": "BBC Tieng Viet",
        "base_url": "https://www.bbc.com/vietnamese",
        "crawl_type": "http",
    },
]


async def seed_sources_if_empty() -> None:
    collections = get_collections()
    source_count = await collections["sources"].count_documents({})
    if source_count > 0:
        return

    now = datetime.now(UTC)
    seed_documents = []
    for item in SEED_SOURCES:
        seed_documents.append(
            {
                "name": item["name"],
                "base_url": item["base_url"],
                "crawl_type": item["crawl_type"],
                "selector_type": "css",
                "selectors": item.get("selectors") or _empty_selectors(),
                "is_active": True,
                "last_crawled": None,
                "created_at": now,
            }
        )

    if seed_documents:
        await collections["sources"].insert_many(seed_documents)
