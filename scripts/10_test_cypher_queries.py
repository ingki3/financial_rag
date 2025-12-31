"""
Cypher Query 생성 테스트 스크립트

질의에 따라 생성되는 Cypher 쿼리를 확인합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import logging
from app.services.query_engine import QueryEngine
from app.services.cypher_query_builder import CypherQueryBuilder

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_cypher_queries():
    """Cypher 쿼리 생성 테스트"""
    
    # 테스트 질의 목록
    test_queries = [
        "애플의 기회 요소에 대해 설명해줘",
        "테슬라의 리스크는?",
        "구글의 AI 기술에 대해 알려줘",
        "애플의 iPhone 15와 관련된 기회 요소는?",
        "구글의 Tim Cook이 언급된 기회 요소는?",
        "애플의 2023년 사업상 리스크는?",
    ]
    
    # QueryEngine 초기화
    print("=" * 80)
    print("Cypher Query 생성 테스트")
    print("=" * 80)
    
    try:
        engine = QueryEngine()
        query_builder = CypherQueryBuilder()
        
        print("\n✅ QueryEngine 초기화 완료\n")
        
        # 각 질의 테스트
        for i, query in enumerate(test_queries, 1):
            print("=" * 80)
            print(f"테스트 {i}/{len(test_queries)}: {query}")
            print("=" * 80)
            
            try:
                # Intent 추출
                intent = engine.extract_intent(query)
                
                print("\n📋 Intent:")
                import json
                print(json.dumps(intent, ensure_ascii=False, indent=2))
                
                # Cypher 쿼리 생성
                cypher_query, params = query_builder.build_query(intent)
                
                print("\n🔍 생성된 Cypher Query:")
                print("-" * 80)
                print(cypher_query)
                print("-" * 80)
                
                print("\n📝 Query Parameters:")
                print("-" * 80)
                print(json.dumps(params, ensure_ascii=False, indent=2))
                print("-" * 80)
                
                # 실제 쿼리 실행 (선택적)
                print("\n🔎 Graph 검색 실행:")
                try:
                    results = engine.graph_search(intent)
                    print(f"  결과: {len(results)}개")
                    if results:
                        print("\n  상위 3개 결과:")
                        for j, res in enumerate(results[:3], 1):
                            print(f"    {j}. {json.dumps(res, ensure_ascii=False, indent=2)}")
                    else:
                        print("  결과 없음")
                except Exception as e:
                    print(f"  ❌ 오류: {e}")
                
            except Exception as e:
                logger.error(f"질의 처리 실패: {e}", exc_info=True)
                print(f"\n❌ 오류 발생: {e}\n")
            
            print("\n")
        
        # 리소스 정리
        engine.close()
        print("=" * 80)
        print("✅ 테스트 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"QueryEngine 초기화 실패: {e}", exc_info=True)
        print(f"\n❌ 초기화 실패: {e}\n")
        return


if __name__ == "__main__":
    test_cypher_queries()


