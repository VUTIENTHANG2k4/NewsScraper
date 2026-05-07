import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from bson import ObjectId

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.mongo import close_mongo_connection, connect_to_mongo, get_collections
from scraper.engine import crawl_one_source

REPORT_JSON_PATH = Path(__file__).resolve().parents[2] / "reports" / "e2e_add_source_cycle_report.json"
REPORT_MD_PATH = Path(__file__).resolve().parents[2] / "reports" / "e2e_add_source_cycle_report.md"


def build_markdown_report(report: dict) -> str:
    lines = [
        "# E2E Add Source Cycle Report",
        "",
        f"- Run at (UTC): `{report['run_at_utc']}`",
        f"- Source inserted: `{report['source_inserted']}`",
        f"- Crawl triggered: `{report['crawl_triggered']}`",
        f"- Crawl log status: `{report['crawl_log_status']}`",
        f"- News found for source: `{report['news_found_for_source']}`",
        f"- Pass: `{report['pass']}`",
        f"- Elapsed: `{report['elapsed_ms']} ms`",
        "",
        "## Notes",
        "",
        "- Test validates the end-to-end chain: add source -> crawl cycle -> news appears.",
        "- In production scheduler, this cycle is executed every 30 minutes.",
        "",
    ]
    if report.get("error"):
        lines.append(f"- Error: `{report['error']}`")
    return "\n".join(lines).strip() + "\n"


def build_temp_source() -> dict:
    unique_suffix = int(time.time())
    return {
        "name": f"E2E Temp Source {unique_suffix}",
        "base_url": f"https://vnexpress.net/goc-nhin?e2e={unique_suffix}",
        "crawl_type": "http",
        "selector_type": "css",
        "selectors": {
            "article_list": "a[href^='https://vnexpress.net/']",
            "title": "title",
            "author": "meta[name='author']",
            "content": "body",
            "published_at": "time",
            "image": "meta[property='og:image']",
            "date_format": "",
        },
        "is_active": True,
        "last_crawled": None,
        "created_at": datetime.now(UTC),
    }


async def main() -> None:
    started = time.perf_counter()
    report = {
        "run_at_utc": datetime.now(UTC).isoformat(),
        "source_inserted": False,
        "crawl_triggered": False,
        "crawl_log_status": None,
        "news_found_for_source": 0,
        "pass": False,
        "elapsed_ms": 0,
        "error": None,
    }

    inserted_source_id: ObjectId | None = None

    try:
        await connect_to_mongo()
        collections = get_collections()

        source_doc = build_temp_source()
        insert_result = await collections["sources"].insert_one(source_doc)
        inserted_source_id = insert_result.inserted_id
        report["source_inserted"] = True

        source_log = await crawl_one_source(str(inserted_source_id))
        report["crawl_triggered"] = True
        if source_log:
            report["crawl_log_status"] = source_log.get("status")

        report["news_found_for_source"] = await collections["news"].count_documents(
            {"source_id": str(inserted_source_id)}
        )
        report["pass"] = report["news_found_for_source"] > 0
    except Exception as error:  # noqa: BLE001
        report["error"] = str(error)
    finally:
        report["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
        REPORT_JSON_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        REPORT_MD_PATH.write_text(build_markdown_report(report), encoding="utf-8")

        if inserted_source_id is not None:
            collections = get_collections()
            await collections["news"].delete_many({"source_id": str(inserted_source_id)})
            await collections["crawl_logs"].delete_many({"source_id": str(inserted_source_id)})
            await collections["sources"].delete_one({"_id": inserted_source_id})

        await close_mongo_connection()

    print(f"Report JSON: {REPORT_JSON_PATH}")
    print(f"Report MD: {REPORT_MD_PATH}")
    print(
        "Summary:",
        f"inserted={report['source_inserted']}, crawl={report['crawl_triggered']},",
        f"news={report['news_found_for_source']}, pass={report['pass']}",
    )


if __name__ == "__main__":
    asyncio.run(main())
