#!/usr/bin/env python
"""Graphiti 자연어 질의 테스트 스크립트.

예)
  python scripts/06_query_graph.py --group-id AAPL --query "애플의 기회 요소는 뭐야?" --limit 10
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graphiti_manager import GraphitiManager


def _json_default(o):
    # Graphiti 결과는 Pydantic 모델/클래스가 섞여 올 수 있어 안전 변환
    if hasattr(o, "model_dump"):
        try:
            return o.model_dump()
        except Exception:
            pass
    if hasattr(o, "dict"):
        try:
            return o.dict()
        except Exception:
            pass
    if hasattr(o, "__dict__"):
        try:
            return dict(o.__dict__)
        except Exception:
            pass
    return str(o)


async def main_async(group_id: str | None, query: str, limit: int):
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    await manager.initialize()
    try:
        group_ids = [group_id] if group_id else None
        results = await manager.search(query=query, group_ids=group_ids, num_results=limit)
        print(json.dumps(results, ensure_ascii=False, indent=2, default=_json_default))
    finally:
        await manager.close()


def main():
    ap = argparse.ArgumentParser(description="Graphiti NLQ Test")
    ap.add_argument("--group-id", type=str, default=None, help="예: AAPL (미지정 시 전체)")
    ap.add_argument("--query", type=str, required=True, help="자연어 질의")
    ap.add_argument("--limit", type=int, default=10, help="반환 개수")
    args = ap.parse_args()
    asyncio.run(main_async(args.group_id, args.query, args.limit))


if __name__ == "__main__":
    main()


