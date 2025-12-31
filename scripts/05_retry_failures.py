#!/usr/bin/env python
"""failure report 기반으로 저장 실패한 episode만 재시도하는 스크립트.

대상:
- `test_result/failures/*.json` (GraphitiManager.add_extracted_triplets에서 생성)

동작:
- failure report의 source_file(extracted triplets json)를 읽어서,
  실패한 항목의 entity/metric을 찾아 동일한 EpisodeData를 재구성하고 add_episode로 재시도.
- 성공하면 해당 failure를 report에서 제거.
- 모든 failure가 해결되면 report를 `test_result/failures_resolved/`로 이동.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graphiti_manager import GraphitiManager, EpisodeData


def _parse_episode_key(name: str) -> tuple[str, str] | None:
    # "AAPL Risk: <entity>" -> ("Risk", "<entity>")
    if ":" not in name:
        return None
    left, right = name.split(":", 1)
    key = left.strip().split()[-1]  # Opportunity/Risk/Event/Strategy/Financial
    entity = right.strip()
    return key, entity


def _category_to_field(category: str) -> str:
    # failures report category uses plural keys from GraphitiManager stats
    return category


def _field_to_label(field: str) -> str:
    return {
        "opportunities": "Opportunity",
        "risks": "Risk",
        "events": "Event",
        "strategies": "Strategy",
        "financials": "Financial",
    }[field]


async def retry_report(report_path: Path, manager: GraphitiManager, delay: float = 1.0) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    source_file = Path(report["source_file"])
    data = json.loads(source_file.read_text(encoding="utf-8"))

    ticker = data.get("ticker", report.get("ticker", ""))
    filing_type = data.get("filing_type", report.get("filing_type", ""))
    accession = data.get("accession_number", report.get("accession_number", ""))
    section = data.get("section", report.get("section", ""))

    year = manager._extract_year_from_accession(accession)
    ref_time = datetime(year, 12, 31) if year else datetime.now()
    source_base = f"SEC {filing_type} - {ticker} ({year}), Section: {section}"

    failures = report.get("failures", [])
    remaining: list[dict] = []
    retried = 0
    succeeded = 0

    # Build quick lookup for each field by entity/metric
    lookups: dict[str, dict[str, dict]] = {}
    for field in ["opportunities", "risks", "events", "strategies"]:
        lookups[field] = {item.get("entity", ""): item for item in data.get(field, [])}
    lookups["financials"] = {item.get("metric", ""): item for item in data.get("financials", [])}

    for f in failures:
        field = _category_to_field(f.get("category", ""))
        ep_name = f.get("name", "")
        parsed = _parse_episode_key(ep_name)
        if not parsed:
            remaining.append(f)
            continue

        _, entity_or_metric = parsed
        item = lookups.get(field, {}).get(entity_or_metric)
        if not item:
            remaining.append(f)
            continue

        label = _field_to_label(field)
        # Reconstruct episode body exactly like GraphitiManager.add_extracted_triplets
        if field == "events":
            event_date = item.get("date", "")
            event_time = manager._parse_date(event_date) or ref_time
            episode = EpisodeData(
                name=f"{ticker} {label}: {item['entity']}",
                body=f"{item['entity']} ({event_date}): {item['description']}",
                source=source_base,
                reference_time=event_time,
                group_id=ticker,
            )
        elif field == "financials":
            period = item.get("period", "")
            episode = EpisodeData(
                name=f"{ticker} {label}: {item['metric']}",
                body=f"{item['metric']}: {item['value']} ({period})",
                source=source_base,
                reference_time=ref_time,
                group_id=ticker,
            )
        else:
            episode = EpisodeData(
                name=f"{ticker} {label}: {item['entity']}",
                body=f"{item['entity']}: {item['description']}",
                source=source_base,
                reference_time=ref_time,
                group_id=ticker,
            )

        retried += 1
        ok = await manager.add_episode(episode)
        if ok:
            succeeded += 1
        else:
            remaining.append(f)
        await asyncio.sleep(delay)

    report["failures"] = remaining
    report["retried_at"] = datetime.now().isoformat()
    report["retry_stats"] = {"retried": retried, "succeeded": succeeded, "remaining": len(remaining)}

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not remaining:
        resolved_dir = Path("./test_result/failures_resolved")
        resolved_dir.mkdir(parents=True, exist_ok=True)
        dest = resolved_dir / report_path.name
        report_path.replace(dest)
        return {"report": str(report_path), "resolved": True, **report["retry_stats"], "moved_to": str(dest)}

    return {"report": str(report_path), "resolved": False, **report["retry_stats"]}


async def main_async():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", type=str, help="예: AAPL (지정 시 해당 티커만)")
    ap.add_argument("--delay", type=float, default=1.0, help="재시도 간 딜레이(초)")
    args = ap.parse_args()

    failures_dir = Path("./test_result/failures")
    reports = sorted(failures_dir.glob("*.json"))
    if args.ticker:
        t = args.ticker.upper()
        reports = [p for p in reports if p.name.startswith(f"{t}_")]

    if not reports:
        print("No failure reports found.")
        return

    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    await manager.initialize()
    try:
        results = []
        for report_path in reports:
            r = await retry_report(report_path, manager, delay=args.delay)
            results.append(r)
            print(json.dumps(r, ensure_ascii=False))
    finally:
        await manager.close()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()


