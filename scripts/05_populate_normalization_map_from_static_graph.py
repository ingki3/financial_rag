"""
Static Graph에서 Normalization Map 생성 스크립트

모든 티커의 static_graph.json 파일을 읽어서
Product와 Person 노드 정보를 normalization_map에 추가합니다.
"""

import json
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


def populate_from_extracted_data(ticker: str, extracted_dir: Path, loader: NormalizationMapLoader):
    """Extracted 데이터에서 Normalization Map 생성
    
    Args:
        ticker: 티커 심볼
        extracted_dir: Extracted 데이터 디렉토리
        loader: NormalizationMapLoader 인스턴스
    """
    if not extracted_dir.exists():
        logger.warning(f"Extracted directory not found: {extracted_dir}")
        return
    
    extracted_files = list(extracted_dir.rglob("*.json"))
    if not extracted_files:
        logger.warning(f"No extracted files found for {ticker}")
        return
    
    all_products = {}
    all_persons = {}
    
    # 모든 extracted 파일에서 수집
    for extracted_file in extracted_files:
        try:
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # mentioned_products_global 수집
            products_global = data.get("mentioned_products_global", [])
            for product in products_global:
                product_name = product.get("name", "").strip()
                if not product_name:
                    continue
                
                name_key = product_name.lower()
                if name_key not in all_products:
                    all_products[name_key] = product
            
            # mentioned_persons_global 수집
            persons_global = data.get("mentioned_persons_global", [])
            for person in persons_global:
                person_name = person.get("name", "").strip()
                if not person_name:
                    continue
                
                name_key = person_name.lower()
                if name_key not in all_persons:
                    all_persons[name_key] = person
                    
        except Exception as e:
            logger.warning(f"Error reading {extracted_file}: {e}")
            continue
    
    logger.info(f"Processing {ticker}: {len(all_products)} products, {len(all_persons)} persons")
    
    # Product 처리
    from app.services.processing.graph_generator import normalize_product_name, is_non_product
    
    for product_name, product_data in all_products.items():
        # 제품이 아닌 항목 필터링
        if is_non_product(product_name, ticker):
            continue
        
        # 제품명 정규화
        normalized_name = normalize_product_name(product_name, ticker)
        if normalized_name is None:
            continue
        
        # 표준명으로 variant 추가
        name_lower = product_name.lower().strip()
        normalized_lower = normalized_name.lower().strip()
        
        loader.add_variant(
            ticker=ticker,
            node_type="Product",
            standard_item=normalized_name,
            variant=name_lower,
            source="extracted_data"
        )
        
        # 정규화된 이름도 variant로 추가 (다를 경우)
        if normalized_lower != name_lower:
            loader.add_variant(
                ticker=ticker,
                node_type="Product",
                standard_item=normalized_name,
                variant=normalized_lower,
                source="extracted_data"
            )
    
    # Person 처리
    for person_name, person_data in all_persons.items():
        # 표준명으로 variant 추가
        name_lower = person_name.lower().strip()
        standard_name = person_data.get("name", person_name).strip()
        
        loader.add_variant(
            ticker=ticker,
            node_type="Person",
            standard_item=standard_name,
            variant=name_lower,
            source="extracted_data"
        )
    
    # 저장
    loader.save(ticker)
    logger.info(f"✅ Updated normalization_map for {ticker}")


def populate_from_static_graph(ticker: str, static_graph_path: Path, loader: NormalizationMapLoader):
    """Static Graph에서 Normalization Map 생성 (보조)
    
    Args:
        ticker: 티커 심볼
        static_graph_path: Static Graph JSON 파일 경로
        loader: NormalizationMapLoader 인스턴스
    """
    if not static_graph_path.exists():
        return
    
    try:
        with open(static_graph_path, 'r', encoding='utf-8') as f:
            static_graph = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load static graph for {ticker}: {e}")
        return
    
    nodes = static_graph.get("nodes", {})
    products = nodes.get("Product", [])
    persons = nodes.get("Person", [])
    
    if products or persons:
        logger.info(f"  Also found in static graph: {len(products)} products, {len(persons)} persons")
    
    # Product 노드 처리
    for product in products:
        product_name = product.get("name", "").strip()
        if not product_name:
            continue
        
        name_lower = product_name.lower().strip()
        loader.add_variant(
            ticker=ticker,
            node_type="Product",
            standard_item=product_name,
            variant=name_lower,
            source="static_graph"
        )
    
    # Person 노드 처리
    for person in persons:
        person_name = person.get("name", "").strip()
        if not person_name:
            continue
        
        name_lower = person_name.lower().strip()
        loader.add_variant(
            ticker=ticker,
            node_type="Person",
            standard_item=person_name,
            variant=name_lower,
            source="static_graph"
        )


def main():
    """메인 함수"""
    tickers = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]
    loader = NormalizationMapLoader()
    
    logger.info("=" * 60)
    logger.info("Extracted 데이터에서 Normalization Map 생성")
    logger.info("=" * 60)
    
    for ticker in tickers:
        logger.info(f"\n🚀 Processing {ticker}...")
        
        # 1. Extracted 데이터에서 추출
        extracted_dir = Path(f"data/extracted/{ticker}")
        populate_from_extracted_data(ticker, extracted_dir, loader)
        
        # 2. Static Graph에서도 확인 (보조)
        static_graph_path = Path(f"data/graph/{ticker}_static_graph.json")
        populate_from_static_graph(ticker, static_graph_path, loader)
        
        # 최종 저장
        loader.save(ticker)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All normalization maps updated!")
    logger.info("=" * 60)
    
    # 요약 출력
    logger.info("\n📊 Summary:")
    for ticker in tickers:
        data = loader.load(ticker)
        categories = data.get("categories", [])
        total_items = sum(len(c.get("standard_items", [])) for c in categories)
        total_mappings = sum(len(c.get("normalized_map", [])) for c in categories)
        total_variants = sum(
            len(item.get("variants", []))
            for cat in categories
            for item in cat.get("normalized_map", [])
        )
        logger.info(f"  {ticker}: {len(categories)} categories, {total_items} items, {total_mappings} mappings, {total_variants} variants")


if __name__ == "__main__":
    main()

