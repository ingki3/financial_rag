"""
각 질의별 Cypher 쿼리 생성 결과 표시

다양한 질의에 대해 생성된 Cypher 쿼리를 보기 좋게 출력합니다.
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
import json
from app.services.query_engine import QueryEngine
from app.services.cypher_query_builder import CypherQueryBuilder

# 로깅 설정 (INFO 레벨로 하면 너무 많은 로그)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def show_cypher_queries():
    """각 질의별 Cypher 쿼리 표시"""
    
    # 다양한 패턴의 테스트 질의
    test_queries = [
        ("애플의 기회 요소는?", "기본 - Company만"),
        ("테슬라의 리스크는?", "기본 - Company만"),
        ("구글의 기술은?", "기본 - Company만"),
        ("애플의 iPhone과 관련된 기회 요소는?", "Product 필터"),
        ("애플의 Mac과 관련된 리스크는?", "Product 필터"),
        ("구글의 AI 기술에 대해 알려줘", "Technology 필터"),
        ("애플의 2023년 기회 요소는?", "시간 필터"),
        ("테슬라의 최근 리스크는?", "시간 필터"),
        ("애플의 2023년 iPhone과 관련된 기회 요소는?", "복합 - 시간 + Product"),
        ("애플과 테슬라의 리스크를 비교해줘", "비교 질의"),
    ]
    
    print("=" * 80)
    print("각 질의별 Cypher 쿼리 생성 결과")
    print("=" * 80)
    
    try:
        engine = QueryEngine()
        query_builder = CypherQueryBuilder()
        
        print("\n✅ QueryEngine 초기화 완료\n")
        
        for i, (query, category) in enumerate(test_queries, 1):
            print("=" * 80)
            print(f"[{i}] {category}")
            print(f"질의: {query}")
            print("=" * 80)
            
            try:
                # Intent 추출
                intent = engine.extract_intent(query)
                
                # Cypher 쿼리 생성
                cypher_query, params = query_builder.build_query(intent)
                
                # Intent 요약
                target_type = intent.get("target_entity_type", "unknown")
                filters = intent.get("filters", {})
                query_type = intent.get("query_type", "unknown")
                
                print(f"\n📋 Intent:")
                print(f"   Target: {target_type}")
                print(f"   Query Type: {query_type}")
                print(f"   Filters: {json.dumps(filters, ensure_ascii=False, indent=2)}")
                
                # 생성된 Cypher 쿼리
                print(f"\n🔍 생성된 Cypher Query:")
                print("-" * 80)
                # 쿼리를 보기 좋게 포맷팅
                formatted_query = cypher_query.replace("MATCH ", "\nMATCH ").replace(" WHERE ", "\nWHERE ").replace(" RETURN ", "\nRETURN ").replace(" ORDER BY ", "\nORDER BY ").replace(" LIMIT ", "\nLIMIT ")
                print(formatted_query)
                print("-" * 80)
                
                # 파라미터
                print(f"\n📝 Query Parameters:")
                print("-" * 80)
                print(json.dumps(params, ensure_ascii=False, indent=2))
                print("-" * 80)
                
                # 쿼리 실행 결과 (간단히)
                try:
                    results = engine.graph_search(intent)
                    print(f"\n✅ 실행 결과: {len(results)}개")
                    if results:
                        print(f"   상위 3개:")
                        for j, res in enumerate(results[:3], 1):
                            entity = res.get("target.entity") or res.get("entity") or res.get("target.id", "N/A")
                            print(f"     {j}. {entity}")
                except Exception as e:
                    print(f"\n❌ 쿼리 실행 오류: {e}")
                
            except Exception as e:
                logger.error(f"질의 처리 실패: {e}", exc_info=True)
                print(f"\n❌ 오류 발생: {e}\n")
            
            print("\n")
        
        engine.close()
        
        print("=" * 80)
        print("✅ 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"초기화 실패: {e}", exc_info=True)
        print(f"\n❌ 초기화 실패: {e}\n")


if __name__ == "__main__":
    show_cypher_queries()


