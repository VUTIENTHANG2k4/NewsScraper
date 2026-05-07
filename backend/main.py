from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_crawl import router as crawl_router
from api.routes_news import router as news_router
from api.routes_sources import router as sources_router
from db.mongo import close_mongo_connection, connect_to_mongo
from db.seed import seed_sources_if_empty
from scraper.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    await seed_sources_if_empty()
    start_scheduler()
    yield
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
    from db.mongo import client
    mongo_status = "disconnected"
    if client:
        try:
            # The ismaster command is cheap and does not require auth.
            await client.admin.command('ismaster')
            mongo_status = "connected"
        except Exception:
            mongo_status = "error"
    return {"status": "ok", "mongodb": mongo_status}
