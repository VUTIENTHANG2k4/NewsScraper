from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from scraper.engine import crawl_active_sources

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        crawl_active_sources,
        "interval",
        minutes=settings.crawl_interval_minutes,
        id="crawl_active_sources",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
