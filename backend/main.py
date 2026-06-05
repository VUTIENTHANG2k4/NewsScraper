import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_crawl import router as crawl_router
from api.routes_news import router as news_router
from api.routes_sources import router as sources_router
from config import settings
from db.mongo import close_mongo_connection, connect_to_mongo
from db.seed import seed_sources_if_empty
from scraper.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Lỗi ở startup phải làm app fail nhanh để Docker/orchestrator restart,
    # tránh trạng thái "app up nhưng scheduler chết / Mongo chưa kết nối".
    await connect_to_mongo()
    await seed_sources_if_empty()
    start_scheduler()
    logger.info("Application started, scheduler running.")
    try:
        yield
    finally:
        stop_scheduler()
        await close_mongo_connection()


app = FastAPI(title="News Scraper API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(crawl_router, prefix="/api/v1")


@app.get("/health")
async def healthcheck() -> dict:
    from db import mongo as mongo_module

    mongo_status = "disconnected"
    if mongo_module.client is not None:
        try:
            await mongo_module.client.admin.command("ping")
            mongo_status = "connected"
        except Exception:  # noqa: BLE001
            mongo_status = "error"
    return {"status": "ok", "mongodb": mongo_status}
