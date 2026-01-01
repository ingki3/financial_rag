"""
Normalization Integration Test

Phase 5 통합 테스트: Graph 생성 및 질의 처리에서 정규화 서비스 사용 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.shared.normalization_service import NormalizationService
from app.services.processing.graph_generator import normalize_product_name
from app.services.shared.name_normalizer import NameNormalizer


def test_normalization_service():
    """NormalizationService 기본 테스트"""
    print("=" * 60)
    print("Test 1: NormalizationService 기본 테스트")
    print("=" * 60)
    
    service = NormalizationService()
    
    # 테스트 케이스
    test_cases = [
        ("iphone", "Product", "AAPL"),
        ("iPhone 15", "Product", "AAPL"),
        ("tim cook", "Person", "AAPL"),
    ]
    
    for name, node_type, ticker in test_cases:
        result = service.normalize(name, node_type, ticker, use_llm=False, auto_save=False)
        print(f"  Input: '{name}' ({node_type}, {ticker})")
        print(f"  Output: '{result}'")
        print()


def test_graph_generator_integration():
    """Graph 생성 통합 테스트"""
    print("=" * 60)
    print("Test 2: Graph 생성 통합 테스트 (normalize_product_name)")
    print("=" * 60)
    
    test_cases = [
        ("iphone", "AAPL"),
        ("iPhone 15 Pro", "AAPL"),
        ("model 3", "TSLA"),
        ("tesla model s", "TSLA"),
    ]
    
    for name, ticker in test_cases:
        result = normalize_product_name(name, ticker)
        print(f"  Input: '{name}' (ticker: {ticker})")
        print(f"  Output: '{result}'")
        print()


def test_query_integration():
    """질의 처리 통합 테스트"""
    print("=" * 60)
    print("Test 3: 질의 처리 통합 테스트 (NameNormalizer.normalize)")
    print("=" * 60)
    
    normalizer = NameNormalizer()
    
    test_cases = [
        ("iphone", "Product", "AAPL"),
        ("iPhone 15 Pro", "Product", "AAPL"),
        ("tim cook", "Person", "AAPL"),
    ]
    
    for name, node_type, ticker in test_cases:
        result = normalizer.normalize(name, node_type, ticker, use_llm=False)
        print(f"  Input: '{name}' ({node_type}, {ticker})")
        print(f"  Output: '{result}'")
        print()


def test_normalization_map_creation():
    """Normalization Map 파일 생성 테스트"""
    print("=" * 60)
    print("Test 4: Normalization Map 파일 생성 테스트")
    print("=" * 60)
    
    from app.services.shared.normalization_map_loader import NormalizationMapLoader
    
    loader = NormalizationMapLoader()
    
    # 테스트 티커
    ticker = "AAPL"
    
    # Map 로드
    data = loader.load(ticker)
    print(f"  Loaded map for {ticker}")
    print(f"  Categories: {len(data.get('categories', []))}")
    
    # Variant 추가 테스트
    loader.add_variant(ticker, "Product", "iPhone", "iphone", source="manual")
    loader.add_variant(ticker, "Product", "iPhone 15", "iphone 15", source="manual")
    
    # 저장
    success = loader.save(ticker)
    print(f"  Save result: {success}")
    
    # 다시 로드하여 확인
    data2 = loader.load(ticker)
    category = loader.get_category(ticker, "Product")
    if category:
        print(f"  Product category found")
        print(f"  Standard items: {len(category.get('standard_items', []))}")
        print(f"  Normalized map entries: {len(category.get('normalized_map', []))}")
    
    print()


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("Phase 5: Normalization Integration Test")
    print("=" * 60 + "\n")
    
    try:
        test_normalization_service()
        test_graph_generator_integration()
        test_query_integration()
        test_normalization_map_creation()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

