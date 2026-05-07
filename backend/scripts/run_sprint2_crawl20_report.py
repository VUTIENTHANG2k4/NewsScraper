import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from pymongo.errors import PyMongoError

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.mongo import close_mongo_connection, connect_to_mongo, get_collections
from db.seed import seed_sources_if_empty
from scraper.engine import crawl_active_sources

REPORT_JSON_PATH = Path(__file__).resolve().parents[2] / "reports" / "sprint2_crawl20_report.json"
REPORT_MD_PATH = Path(__file__).resolve().parents[2] / "reports" / "sprint2_crawl20_report.md"


def build_markdown_report(report: dict) -> str:
    lines = [
        "# Sprint 2 Crawl Report (20 sources)",
        "",
        f"- Run at (UTC): `{report['run_at_utc']}`",
        f"- Active sources: `{report['active_sources']}`",
        f"- Crawl logs created: `{report['crawl_logs_created']}`",
        f"- Success: `{report['success_count']}`",
        f"- Partial: `{report['partial_count']}`",
        f"- Error: `{report['error_count']}`",
        f"- Elapsed: `{report['elapsed_ms']} ms`",
        "",
        "## Per Source",
        "",
    ]
    for item in report["source_results"]:
        lines.append(f"### {item['source_name']}")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Found/New: `{item['articles_found']}/{item['articles_new']}`")
        lines.append(f"- Crawled at: `{item['crawled_at']}`")
        if item.get("error_msg"):
            lines.append(f"- Error: `{item['error_msg']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


async def main() -> None:
    started = time.perf_counter()
    try:
        await connect_to_mongo()
    except Exception as connection_error:  # noqa: BLE001
        raise RuntimeError(
            "Khong ket noi duoc MongoDB. Hay bat MongoDB/Docker truoc khi chay script."
        ) from connection_error

    try:
        await seed_sources_if_empty()
        collections = get_collections()

        active_sources = await collections["sources"].count_documents({"is_active": True})
        logs_before = await collections["crawl_logs"].count_documents({})

        run_logs = await crawl_active_sources()

        logs_after = await collections["crawl_logs"].count_documents({})
        crawl_logs_created = logs_after - logs_before

        success_count = sum(1 for row in run_logs if row.get("status") == "success")
        partial_count = sum(1 for row in run_logs if row.get("status") == "partial")
        error_count = sum(1 for row in run_logs if row.get("status") == "error")

        report = {
            "run_at_utc": datetime.now(UTC).isoformat(),
            "active_sources": active_sources,
            "crawl_logs_created": crawl_logs_created,
            "success_count": success_count,
            "partial_count": partial_count,
            "error_count": error_count,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "source_results": run_logs,
        }

        REPORT_JSON_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        REPORT_MD_PATH.write_text(build_markdown_report(report), encoding="utf-8")

        print(f"Report JSON: {REPORT_JSON_PATH}")
        print(f"Report MD: {REPORT_MD_PATH}")
        print(
            "Summary:",
            f"active_sources={active_sources}, logs_created={crawl_logs_created},",
            f"success={success_count}, partial={partial_count}, error={error_count}",
        )
    except PyMongoError as mongo_error:
        raise RuntimeError(f"Loi MongoDB khi crawl/ghi log: {mongo_error}") from mongo_error
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:  # noqa: BLE001
        print(f"Sprint 2 report failed: {error}")
        raise SystemExit(1) from error
