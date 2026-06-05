"""
Distributed lock đơn giản dựa trên MongoDB.

Cho phép nhiều instance backend chạy song song mà chỉ 1 instance kích hoạt
crawl_active_sources() ở mỗi mốc lập lịch. Cơ chế:

- Mỗi lock là một document trong collection `crawl_locks` với `_id = lock name`.
- Acquire = `insert_one` (hoặc replace nếu document cũ đã hết hạn). Nếu trùng
  `_id` còn hiệu lực sẽ raise DuplicateKeyError.
- TTL index trên field `expires_at` tự xoá document khi hết hạn — bảo đảm
  unlock tự động nếu instance giữ lock crash.
"""

from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from pymongo.errors import DuplicateKeyError

from db.mongo import get_collections


@asynccontextmanager
async def try_acquire(lock_name: str, ttl_seconds: int):
    """
    Cố gắng acquire lock. Yield True nếu chiếm được, False nếu instance khác đang giữ.

    Usage:
        async with try_acquire("crawl_active_sources", ttl_seconds=1800) as got:
            if not got:
                return
            ...do work...
    """
    collections = get_collections()
    locks = collections["crawl_locks"]
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=ttl_seconds)

    acquired = False
    try:
        # Trường hợp document cũ đã hết hạn nhưng TTL chưa quét xong (TTL monitor
        # chạy ~60s/lần) — cần chủ động xoá để insert lại.
        await locks.delete_one({"_id": lock_name, "expires_at": {"$lte": now}})

        try:
            await locks.insert_one(
                {"_id": lock_name, "acquired_at": now, "expires_at": expires_at}
            )
            acquired = True
        except DuplicateKeyError:
            acquired = False

        yield acquired
    finally:
        if acquired:
            await locks.delete_one({"_id": lock_name})
