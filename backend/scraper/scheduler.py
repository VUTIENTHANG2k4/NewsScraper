from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from scraper.engine import crawl_active_sources

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    if scheduler.running:
        return

    # Chạy lần đầu ngay sau khi app khởi động ~5s (đủ để Mongo connection
    # và indexes sẵn sàng), sau đó lặp lại mỗi `crawl_interval_minutes` phút.
    first_run_at = datetime.now(UTC) + timedelta(seconds=5)

    scheduler.add_job(
        crawl_active_sources,
        "interval",
        minutes=settings.crawl_interval_minutes,
        id="crawl_active_sources",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=first_run_at,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
