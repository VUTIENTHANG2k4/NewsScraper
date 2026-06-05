from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from dateutil import parser as date_parser

# Múi giờ giả định cho datetime "naive" (không có tzinfo) parse được từ HTML.
# Vì 100% nguồn đang seed là báo Việt Nam, nếu site trả meta tag dạng
# "2026-06-04T11:07:00" (không kèm timezone) thì gần như chắc chắn là giờ VN.
# Trước đây code gán UTC vào → hiển thị frontend lệch +7h.
_DEFAULT_NAIVE_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def try_parse_datetime(
    raw_date: str | None, date_format: str | None = None
) -> datetime | None:
    """
    Parse raw date string thành datetime UTC. Trả None nếu không parse được —
    để caller có thể quyết định fallback (vd. dùng meta tag thay thế) thay vì
    âm thầm dùng now() khiến `published_at` mất nghĩa.

    Nếu chuỗi không có timezone, mặc định coi là giờ Việt Nam
    (Asia/Ho_Chi_Minh) trước khi quy đổi sang UTC.
    """
    if not raw_date:
        return None
    try:
        parsed = date_parser.parse(raw_date)
    except (ValueError, TypeError, OverflowError):
        if date_format:
            try:
                parsed = datetime.strptime(raw_date, date_format)
            except ValueError:
                return None
        else:
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_DEFAULT_NAIVE_TZ)
    return parsed.astimezone(UTC)


def normalize_datetime(raw_date: str | None, date_format: str | None = None) -> datetime:
    """
    Backward-compatible wrapper: trả `now()` nếu parse fail. Code mới nên dùng
    `try_parse_datetime` để xử lý fallback rõ ràng.
    """
    parsed = try_parse_datetime(raw_date, date_format)
    return parsed if parsed is not None else datetime.now(UTC)


def clean_text(value: str | None, max_length: int = 50000) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return normalized[:max_length]


async def is_duplicate_source_url(news_collection, source_url: str) -> bool:
    existing = await news_collection.find_one({"source_url": source_url}, {"_id": 1})
    return existing is not None
