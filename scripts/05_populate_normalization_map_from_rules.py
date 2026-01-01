"""
기존 하드코딩된 정규화 규칙을 Normalization Map으로 변환

graph_generator.py의 normalize_product_name()에 있는
하드코딩된 정규화 규칙을 normalization_map에 추가합니다.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.shared.normalization_map_loader import NormalizationMapLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 기존 하드코딩된 정규화 규칙
HARDCODED_RULES = {
    "TSLA": {
        "Product": {
            "Tesla Model 3": ["model 3", "tesla model 3"],
            "Tesla Model S": ["model s", "tesla model s"],
            "Tesla Model X": ["model x", "tesla model x"],
            "Tesla Model Y": ["model y", "tesla model y"],
            "Tesla Supercharger": ["supercharger", "superchargers", "tesla supercharger", "tesla superchargers"],
            "Full Self-Driving (FSD)": ["fsd", "full self-driving", "fsd (supervised)"],
            "NACS": ["nacs", "north american charging standard"],
        }
    },
    "AAPL": {
        "Product": {
            # Apple 제품은 일반적으로 브랜드명이 제품명이므로 특별한 매핑이 적음
            # 실제 데이터에서 추출될 때 추가됨
        }
    },
    "GOOGL": {
        "Product": {
            "Google Search": ["search"],
        }
    },
    "MSFT": {
        "Product": {
            "Microsoft Copilot": ["copilot"],
        }
    }
}


def populate_from_hardcoded_rules(loader: NormalizationMapLoader):
    """하드코딩된 규칙을 Normalization Map에 추가"""
    
    logger.info("=" * 60)
    logger.info("하드코딩된 정규화 규칙을 Normalization Map으로 변환")
    logger.info("=" * 60)
    
    for ticker, categories in HARDCODED_RULES.items():
        logger.info(f"\n🚀 Processing {ticker}...")
        
        for node_type, mappings in categories.items():
            for standard_item, variants in mappings.items():
                for variant in variants:
                    loader.add_variant(
                        ticker=ticker,
                        node_type=node_type,
                        standard_item=standard_item,
                        variant=variant.lower().strip(),
                        source="hardcoded_rule"
                    )
        
        loader.save(ticker)
        logger.info(f"✅ Updated normalization_map for {ticker}")
    
    # 요약 출력
    logger.info("\n" + "=" * 60)
    logger.info("📊 Summary:")
    for ticker in HARDCODED_RULES.keys():
        data = loader.load(ticker)
        categories = data.get("categories", [])
        total_items = sum(len(c.get("standard_items", [])) for c in categories)
        total_mappings = sum(len(c.get("normalized_map", [])) for c in categories)
        total_variants = sum(
            len(item.get("variants", []))
            for cat in categories
            for item in cat.get("normalized_map", [])
        )
        logger.info(f"  {ticker}: {total_items} items, {total_mappings} mappings, {total_variants} variants")


if __name__ == "__main__":
    loader = NormalizationMapLoader()
    populate_from_hardcoded_rules(loader)

