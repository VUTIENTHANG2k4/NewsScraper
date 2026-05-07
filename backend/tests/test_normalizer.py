from datetime import UTC, datetime

import pytest

from scraper.normalizer import clean_text, is_duplicate_source_url, normalize_datetime


def test_normalize_datetime_with_timezone() -> None:
    result = normalize_datetime("2026-04-17T10:00:00+07:00")
    assert result.tzinfo == UTC
    assert result.hour == 3


def test_normalize_datetime_with_custom_format() -> None:
    result = normalize_datetime("17/04/2026 10:30", "%d/%m/%Y %H:%M")
    assert result.tzinfo == UTC
    assert result.year == 2026
    assert result.month == 4
    assert result.day == 17


def test_normalize_datetime_invalid_fallback_to_now() -> None:
    before = datetime.now(UTC)
    result = normalize_datetime("invalid date")
    after = datetime.now(UTC)
    assert before <= result <= after


def test_clean_text_trims_and_truncates() -> None:
    raw = "  line 1 \n\t line 2   "
    result = clean_text(raw, max_length=7)
    assert result == "line 1 "


def test_clean_text_returns_none_for_blank() -> None:
    assert clean_text("   \n\t   ") is None


class _FakeNewsCollection:
    def __init__(self, result):
        self.result = result

    async def find_one(self, *_args, **_kwargs):
        return self.result


@pytest.mark.asyncio
async def test_is_duplicate_source_url_true() -> None:
    collection = _FakeNewsCollection({"_id": "abc"})
    assert await is_duplicate_source_url(collection, "https://example.com/a") is True


@pytest.mark.asyncio
async def test_is_duplicate_source_url_false() -> None:
    collection = _FakeNewsCollection(None)
    assert await is_duplicate_source_url(collection, "https://example.com/a") is False
