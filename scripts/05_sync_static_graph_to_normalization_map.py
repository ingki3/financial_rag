"""
Static Graph의 모든 제품을 Normalization Map에 동기화

Static graph에 생성된 모든 Product를 normalization_map에 추가합니다.
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


def sync_static_graph_to_normalization_map(ticker: str):
    """Static Graph의 제품을 Normalization Map에 동기화"""
    
    # Static graph 로드
    static_file = Path(f"data/graph/{ticker}_static_graph.json")
    if not static_file.exists():
        logger.warning(f"Static graph not found: {static_file}")
        return
    
    static_graph = json.load(open(static_file))
    products = static_graph.get('nodes', {}).get('Product', [])
    
    if not products:
        logger.info(f"{ticker}: No products in static graph")
        return
    
    # Normalization map 로드
    map_file = Path(f"data/normalization_maps/{ticker}_normalization_map.json")
    if not map_file.exists():
        logger.warning(f"Normalization map not found: {map_file}")
        return
    
    data = json.load(open(map_file))
    
    # Product 카테고리 찾기 또는 생성
    product_cat = None
    for cat in data.get('categories', []):
        if cat.get('category') == 'Product':
            product_cat = cat
            break
    
    if not product_cat:
        product_cat = {
            'category': 'Product',
            'standard_items': [],
            'normalized_map': []
        }
        data['categories'].append(product_cat)
    
    # 모든 제품 추가
    now = datetime.utcnow().isoformat() + 'Z'
    added_count = 0
    
    for product in products:
        product_name = product.get('name', '').strip()
        if not product_name:
            continue
        
        # standard_items에 추가 (중복 체크)
        if product_name not in product_cat['standard_items']:
            product_cat['standard_items'].append(product_name)
            added_count += 1
        
        # normalized_map에서 찾기
        found = False
        for item in product_cat.get('normalized_map', []):
            if item.get('standard_item') == product_name:
                # variant 추가
                name_lower = product_name.lower().strip()
                if name_lower not in item.get('variants', []):
                    item['variants'].append(name_lower)
                found = True
                break
        
        if not found:
            # 새 항목 추가
            name_lower = product_name.lower().strip()
            normalized_item = {
                'standard_item': product_name,
                'variants': [name_lower],
                'metadata': {
                    'added_at': now,
                    'total_usage_count': 0,
                    'source': 'static_graph'
                }
            }
            product_cat['normalized_map'].append(normalized_item)
    
    # 정렬
    product_cat['standard_items'].sort()
    for item in product_cat.get('normalized_map', []):
        item['variants'].sort()
    
    # 메타데이터 업데이트
    data['metadata']['last_updated'] = now
    data['metadata']['total_mappings'] = len(product_cat.get('normalized_map', []))
    
    # 저장
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ {ticker}: {added_count}개 새 제품 추가, 총 {len(product_cat['standard_items'])}개 제품")


def main():
    """메인 함수"""
    tickers = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]
    
    logger.info("=" * 60)
    logger.info("Static Graph → Normalization Map 동기화")
    logger.info("=" * 60)
    
    for ticker in tickers:
        logger.info(f"\n🚀 Processing {ticker}...")
        sync_static_graph_to_normalization_map(ticker)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 동기화 완료!")
    logger.info("=" * 60)
    
    # 최종 요약
    logger.info("\n📊 최종 현황:")
    for ticker in tickers:
        map_file = Path(f"data/normalization_maps/{ticker}_normalization_map.json")
        if map_file.exists():
            data = json.load(open(map_file))
            cat = data.get('categories', [{}])[0] if data.get('categories') else {}
            items = cat.get('standard_items', [])
            mappings = cat.get('normalized_map', [])
            status = "✅" if len(items) > 0 else "⚪"
            logger.info(f"  {status} {ticker}: {len(items)} items, {len(mappings)} mappings")


if __name__ == "__main__":
    main()

