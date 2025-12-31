#!/usr/bin/env python
"""단일 샘플(1개 filing/section)만 Triplet 추출하여 저장하는 스크립트

목적:
- 새 YAML prompt(app/prompts/triplet_extractor.yaml)가 제대로 동작하는지 빠르게 검증
- 비용/시간을 줄이기 위해 전체 배치가 아니라 1건만 실행
"""

import argparse
import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.services.triplet_extractor import TripletExtractor


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract triplets for a single parsed SEC section.")
    p.add_argument("--ticker", default="AAPL")
    p.add_argument("--filing-type", default="8-K", dest="filing_type")
    p.add_argument(
        "--accession",
        default="0000320193-23-000104",
        help="Accession number (filename without .json) under data/parsed/{ticker}/{filing_type}/",
    )
    p.add_argument("--section", default="results_operations")
    p.add_argument("--parsed-dir", default="./data/parsed")
    p.add_argument("--output-dir", default="./data/extracted")
    p.add_argument("--model", default="gemini-3-flash-preview")
    p.add_argument("--max-chars", type=int, default=0, help="If >0, truncate section text to this many characters.")
    return p.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    parsed_path = (
        Path(args.parsed_dir) / args.ticker / args.filing_type / f"{args.accession}.json"
    )
    if not parsed_path.exists():
        raise FileNotFoundError(f"Parsed file not found: {parsed_path}")

    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    sections = parsed.get("sections", {})
    section_text = sections.get(args.section, "")
    if not section_text:
        raise ValueError(f"Section '{args.section}' not found (or empty) in {parsed_path}")

    if args.max_chars and args.max_chars > 0:
        section_text = section_text[: args.max_chars]

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    extractor = TripletExtractor(model=args.model, api_key=api_key)

    logger.info(
        f"Extracting: ticker={args.ticker}, filing_type={args.filing_type}, accession={args.accession}, section={args.section}, model={args.model}"
    )
    result = extractor.extract(
        text=section_text,
        ticker=args.ticker,
        filing_type=args.filing_type,
        section=args.section,
        accession_number=args.accession,
    )

    output_dir = Path(args.output_dir) / args.ticker / args.filing_type
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{args.accession}_{args.section}.json"

    payload = result.to_dict()
    payload["extracted_at"] = datetime.now().isoformat()
    payload["model"] = args.model
    payload["prompt"] = "app/prompts/triplet_extractor.yaml"
    payload["source_parsed_file"] = str(parsed_path)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Saved: {out_path} (total_items={result.total_count()})")


if __name__ == "__main__":
    main()


