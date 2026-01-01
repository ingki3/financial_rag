"""
Normalization System Full Test

정규화 시스템의 전체 기능을 테스트합니다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.shared.normalization_service import NormalizationService
from app.services.processing.graph_generator import normalize_product_name


def test_normalization_workflow():
    """정규화 워크플로우 테스트"""
    print("=" * 60)
    print("Normalization System Full Test")
    print("=" * 60)
    
    service = NormalizationService()
    
    # 테스트 케이스
    test_cases = [
        # (입력, 노드타입, 티커, 설명)
        ("iphone", "Product", "AAPL", "소문자 입력"),
        ("iPhone 15", "Product", "AAPL", "표준명 입력"),
        ("iPhone 15 Pro", "Product", "AAPL", "표준명 입력"),
        ("model 3", "Product", "TSLA", "Tesla 제품"),
        ("tesla model s", "Product", "TSLA", "Tesla 제품 (소문자)"),
        ("tim cook", "Person", "AAPL", "인물명"),
    ]
    
    print("\n[1] 정규화 테스트 (LLM 비활성화)")
    print("-" * 60)
    for name, node_type, ticker, desc in test_cases:
        result = service.normalize(name, node_type, ticker, use_llm=False, auto_save=True)
        print(f"  {desc:20} | {name:20} → {result}")
    
    print("\n[2] Normalization Map 확인")
    print("-" * 60)
    from app.services.shared.normalization_map_loader import NormalizationMapLoader
    loader = NormalizationMapLoader()
    
    for ticker in ["AAPL", "TSLA"]:
        data = loader.load(ticker)
        categories = data.get("categories", [])
        print(f"\n  {ticker}:")
        for cat in categories:
            cat_name = cat.get("category")
            standard_items = cat.get("standard_items", [])
            normalized_map = cat.get("normalized_map", [])
            print(f"    {cat_name}:")
            print(f"      - Standard items: {len(standard_items)}")
            print(f"      - Normalized map entries: {len(normalized_map)}")
            if normalized_map:
                for item in normalized_map[:3]:  # 처음 3개만
                    std = item.get("standard_item")
                    variants = item.get("variants", [])
                    print(f"        • {std}: {len(variants)} variants")
    
    print("\n[3] Graph 생성 통합 테스트")
    print("-" * 60)
    test_products = [
        ("iphone", "AAPL"),
        ("iPhone 15 Pro", "AAPL"),
        ("model 3", "TSLA"),
    ]
    
    for name, ticker in test_products:
        result = normalize_product_name(name, ticker)
        print(f"  {name:20} ({ticker}) → {result}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_normalization_workflow()

