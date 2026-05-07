from datetime import UTC, datetime

from dateutil import parser as date_parser


def normalize_datetime(raw_date: str | None, date_format: str | None = None) -> datetime:
    now = datetime.now(UTC)
    if not raw_date:
        return now
    try:
        parsed = date_parser.parse(raw_date)
    except (ValueError, TypeError):
        if date_format:
            try:
                parsed = datetime.strptime(raw_date, date_format)
            except ValueError:
                return now
        else:
            return now

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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
