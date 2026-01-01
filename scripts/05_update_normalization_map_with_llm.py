"""
LLM을 활용하여 Normalization Map 업데이트

Static Graph의 모든 제품명을 LLM으로 분석하여:
1. 표준명 제안
2. Variants 발견
3. Normalization Rules 발견
4. Normalization Map 자동 업데이트
"""

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.shared.normalization_service import NormalizationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_normalization_map_with_llm(ticker: str, batch_size: int = 10):
    """LLM을 사용하여 Normalization Map 업데이트
    
    Args:
        ticker: 티커 심볼
        batch_size: 배치 크기 (API 호출 제한 고려)
    """
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
    
    logger.info(f"{ticker}: {len(products)}개 제품을 LLM으로 분석 중...")
    
    # NormalizationService 초기화
    service = NormalizationService()
    
    # 기존 normalization_map 로드 (LLM이 참고할 수 있도록)
    data = service.loader.load(ticker)
    category = service.loader.get_category(ticker, "Product")
    existing_standard_items = category.get("standard_items", []) if category else []
    
    logger.info(f"  기존 표준명: {len(existing_standard_items)}개")
    
    # 각 제품명을 LLM으로 정규화
    processed_count = 0
    new_standards = []
    discovered_rules = []
    
    for i, product in enumerate(products, 1):
        product_name = product.get('name', '').strip()
        if not product_name:
            continue
        
        try:
            # LLM을 사용하여 정규화 (auto_save=True로 설정하여 자동 저장)
            normalized = service.normalize(
                name=product_name,
                node_type="Product",
                ticker=ticker,
                use_llm=True,
                auto_save=False  # 배치로 저장하기 위해 False
            )
            
            if normalized and normalized != product_name:
                logger.info(f"  [{i}/{len(products)}] '{product_name}' → '{normalized}'")
                new_standards.append((product_name, normalized))
            elif normalized:
                logger.debug(f"  [{i}/{len(products)}] '{product_name}' (이미 표준명)")
            else:
                logger.warning(f"  [{i}/{len(products)}] '{product_name}' (정규화 실패)")
            
            processed_count += 1
            
            # 배치 단위로 저장 (API 호출 제한 고려)
            if processed_count % batch_size == 0:
                service.loader.save(ticker)
                logger.info(f"  중간 저장 완료 ({processed_count}/{len(products)})")
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"  Error processing '{product_name}': {e}")
            continue
    
    # 최종 저장
    service.loader.save(ticker)
    
    # 업데이트된 데이터 확인
    updated_data = service.loader.load(ticker)
    updated_category = service.loader.get_category(ticker, "Product")
    updated_standard_items = updated_category.get("standard_items", []) if updated_category else []
    updated_mappings = updated_category.get("normalized_map", []) if updated_category else []
    updated_rules = []
    for rule_group in updated_data.get("normalization_rules", []):
        if rule_group.get("category") == "Product":
            updated_rules = rule_group.get("rules", [])
            break
    
    logger.info(f"✅ {ticker} 완료:")
    logger.info(f"   처리된 제품: {processed_count}개")
    logger.info(f"   표준명: {len(updated_standard_items)}개 (기존 {len(existing_standard_items)}개)")
    logger.info(f"   매핑: {len(updated_mappings)}개")
    logger.info(f"   발견된 규칙: {len(updated_rules)}개")
    
    if new_standards:
        logger.info(f"   새로 추가된 표준명:")
        for original, normalized in new_standards[:5]:  # 처음 5개만
            logger.info(f"     - {original} → {normalized}")
        if len(new_standards) > 5:
            logger.info(f"     ... 외 {len(new_standards) - 5}개")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM을 활용하여 Normalization Map 업데이트")
    parser.add_argument("--ticker", nargs="+", default=["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"],
                        help="처리할 티커 목록")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="배치 크기 (API 호출 제한 고려)")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("LLM을 활용한 Normalization Map 업데이트")
    logger.info("=" * 60)
    logger.info(f"대상 티커: {', '.join(args.ticker)}")
    logger.info(f"배치 크기: {args.batch_size}")
    logger.info("=" * 60)
    
    for ticker in args.ticker:
        logger.info(f"\n🚀 Processing {ticker}...")
        try:
            update_normalization_map_with_llm(ticker.upper(), args.batch_size)
        except Exception as e:
            logger.error(f"❌ {ticker} 처리 중 오류: {e}")
            continue
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 모든 티커 처리 완료!")
    logger.info("=" * 60)
    
    # 최종 요약
    logger.info("\n📊 최종 현황:")
    service = NormalizationService()
    for ticker in args.ticker:
        ticker = ticker.upper()
        data = service.loader.load(ticker)
        category = service.loader.get_category(ticker, "Product")
        if category:
            items = category.get("standard_items", [])
            mappings = category.get("normalized_map", [])
            rules = []
            for rule_group in data.get("normalization_rules", []):
                if rule_group.get("category") == "Product":
                    rules = rule_group.get("rules", [])
                    break
            status = "✅" if len(items) > 0 else "⚪"
            logger.info(f"  {status} {ticker}: {len(items)} items, {len(mappings)} mappings, {len(rules)} rules")
        else:
            logger.info(f"  ⚪ {ticker}: 카테고리 없음")


if __name__ == "__main__":
    main()

