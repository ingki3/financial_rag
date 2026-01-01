"""
모든 티커에 대해 Normalization Map 완전 재생성

기존 하드코딩된 규칙과 static graph를 참고하여
모든 티커의 normalization_map을 생성합니다.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 하드코딩된 정규화 규칙
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
            # iPhone 15는 이미 추가됨
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


def create_normalization_map(ticker: str) -> dict:
    """Normalization Map 생성 (기존 데이터 보존)
    
    Args:
        ticker: 티커 심볼
        
    Returns:
        Normalization Map 딕셔너리
    """
    now = datetime.utcnow().isoformat() + "Z"
    
    # 기존 파일이 있으면 로드
    maps_dir = Path("data/normalization_maps")
    map_file = maps_dir / f"{ticker}_normalization_map.json"
    
    if map_file.exists():
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            # 메타데이터만 업데이트
            map_data["metadata"]["last_updated"] = now
        except Exception as e:
            logger.warning(f"Failed to load existing map for {ticker}: {e}")
            map_data = None
    else:
        map_data = None
    
    # 기존 데이터가 없으면 새로 생성
    if not map_data:
        map_data = {
            "metadata": {
                "ticker": ticker,
                "version": "1.0.0",
                "created_at": now,
                "last_updated": now,
                "total_mappings": 0,
                "llm_generated_count": 0,
                "auto_added_count": 0
            },
            "categories": [],
            "filtered_terms": [],
            "normalization_rules": []
        }
    
    # 하드코딩된 규칙 추가
    if ticker in HARDCODED_RULES:
        for node_type, mappings in HARDCODED_RULES[ticker].items():
            # 기존 카테고리 찾기
            category = None
            for cat in map_data["categories"]:
                if cat.get("category") == node_type:
                    category = cat
                    break
            
            # 없으면 생성
            if not category:
                category = {
                    "category": node_type,
                    "standard_items": [],
                    "normalized_map": []
                }
                map_data["categories"].append(category)
            
            for standard_item, variants in mappings.items():
                # standard_items에 추가 (중복 체크)
                if standard_item not in category["standard_items"]:
                    category["standard_items"].append(standard_item)
                
                # normalized_map에서 기존 항목 찾기
                normalized_item = None
                for item in category["normalized_map"]:
                    if item.get("standard_item") == standard_item:
                        normalized_item = item
                        break
                
                # 없으면 새로 생성
                if not normalized_item:
                    normalized_item = {
                        "standard_item": standard_item,
                        "variants": [],
                        "metadata": {
                            "added_at": now,
                            "total_usage_count": 0,
                            "source": "hardcoded_rule"
                        }
                    }
                    category["normalized_map"].append(normalized_item)
                
                # variants 추가 (중복 체크)
                for variant in variants:
                    variant_lower = variant.lower().strip()
                    if variant_lower not in normalized_item["variants"]:
                        normalized_item["variants"].append(variant_lower)
            
            # 정렬
            if category["standard_items"]:
                category["standard_items"].sort()
            for item in category["normalized_map"]:
                item["variants"].sort()
    
    # Static Graph에서 추가 정보 가져오기
    static_graph_path = Path(f"data/graph/{ticker}_static_graph.json")
    if static_graph_path.exists():
        try:
            with open(static_graph_path, 'r', encoding='utf-8') as f:
                static_graph = json.load(f)
            
            nodes = static_graph.get("nodes", {})
            products = nodes.get("Product", [])
            persons = nodes.get("Person", [])
            
            if products or persons:
                # Product 카테고리 찾기 또는 생성
                product_cat = None
                for cat in map_data["categories"]:
                    if cat.get("category") == "Product":
                        product_cat = cat
                        break
                
                if not product_cat and (products or ticker in HARDCODED_RULES):
                    product_cat = {
                        "category": "Product",
                        "standard_items": [],
                        "normalized_map": []
                    }
                    map_data["categories"].append(product_cat)
                
                # Product 추가
                for product in products:
                    product_name = product.get("name", "").strip()
                    if not product_name:
                        continue
                    
                    if product_name not in product_cat["standard_items"]:
                        product_cat["standard_items"].append(product_name)
                    
                    # normalized_map에 추가
                    name_lower = product_name.lower().strip()
                    normalized_item = {
                        "standard_item": product_name,
                        "variants": [name_lower],
                        "metadata": {
                            "added_at": now,
                            "total_usage_count": 0,
                            "source": "static_graph"
                        }
                    }
                    product_cat["normalized_map"].append(normalized_item)
                
                # Person 카테고리
                if persons:
                    person_cat = {
                        "category": "Person",
                        "standard_items": [],
                        "normalized_map": []
                    }
                    
                    for person in persons:
                        person_name = person.get("name", "").strip()
                        if not person_name:
                            continue
                        
                        person_cat["standard_items"].append(person_name)
                        name_lower = person_name.lower().strip()
                        normalized_item = {
                            "standard_item": person_name,
                            "variants": [name_lower],
                            "metadata": {
                                "added_at": now,
                                "total_usage_count": 0,
                                "source": "static_graph"
                            }
                        }
                        person_cat["normalized_map"].append(normalized_item)
                    
                    if person_cat["standard_items"]:
                        person_cat["standard_items"].sort()
                        map_data["categories"].append(person_cat)
                        
        except Exception as e:
            logger.warning(f"Failed to load static graph for {ticker}: {e}")
    
    # 메타데이터 업데이트
    total_mappings = sum(len(c.get("normalized_map", [])) for c in map_data["categories"])
    map_data["metadata"]["total_mappings"] = total_mappings
    
    return map_data


def main():
    """메인 함수"""
    tickers = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]
    maps_dir = Path("data/normalization_maps")
    maps_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("모든 티커에 대해 Normalization Map 재생성")
    logger.info("=" * 60)
    
    for ticker in tickers:
        logger.info(f"\n🚀 Processing {ticker}...")
        
        # Normalization Map 생성
        map_data = create_normalization_map(ticker)
        
        # 파일 저장
        map_file = maps_dir / f"{ticker}_normalization_map.json"
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        
        # 요약 출력
        categories = map_data.get("categories", [])
        total_items = sum(len(c.get("standard_items", [])) for c in categories)
        total_mappings = sum(len(c.get("normalized_map", [])) for c in categories)
        total_variants = sum(
            len(item.get("variants", []))
            for cat in categories
            for item in cat.get("normalized_map", [])
        )
        logger.info(f"✅ {ticker}: {len(categories)} categories, {total_items} items, {total_mappings} mappings, {total_variants} variants")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All normalization maps regenerated!")
    logger.info("=" * 60)
    
    # 최종 요약
    logger.info("\n📊 Final Summary:")
    for ticker in tickers:
        map_file = maps_dir / f"{ticker}_normalization_map.json"
        if map_file.exists():
            with open(map_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            categories = data.get("categories", [])
            total_items = sum(len(c.get("standard_items", [])) for c in categories)
            total_mappings = sum(len(c.get("normalized_map", [])) for c in categories)
            total_variants = sum(
                len(item.get("variants", []))
                for cat in categories
                for item in cat.get("normalized_map", [])
            )
            status = "✅" if total_items > 0 else "⚪"
            logger.info(f"  {status} {ticker}: {total_items} items, {total_mappings} mappings, {total_variants} variants")


if __name__ == "__main__":
    main()

