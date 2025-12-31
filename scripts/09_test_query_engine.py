"""
Phase 8 Query Engine 테스트 스크립트

질의 응답 시스템의 전체 흐름을 테스트합니다.
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
from app.services.answer_generator import AnswerGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_query_engine():
    """QueryEngine 테스트"""
    
    # 테스트 질의 목록
    test_queries = [
        "애플의 기회 요소에 대해 설명해줘",
        "테슬라의 리스크는?",
        "구글의 AI 기술에 대해 알려줘",
        "애플의 iPhone 15와 관련된 기회 요소는?",
    ]
    
    # QueryEngine 초기화
    print("=" * 80)
    print("QueryEngine 초기화 중...")
    print("=" * 80)
    
    try:
        engine = QueryEngine()
        try:
            answer_generator = AnswerGenerator()
        except Exception as e:
            logger.warning(f"AnswerGenerator 초기화 실패: {e}")
            answer_generator = None
        
        print("\n✅ QueryEngine 초기화 완료\n")
        
        # 각 질의 테스트
        for i, query in enumerate(test_queries, 1):
            print("=" * 80)
            print(f"테스트 {i}/{len(test_queries)}: {query}")
            print("=" * 80)
            
            try:
                # 질의 처리
                result = engine.query(
                    user_query=query,
                    top_k=5,
                    use_vector_search=True,
                    use_graph_search=True
                )
                
                # Intent 출력
                print("\n📋 Intent:")
                import json
                print(json.dumps(result["intent"], ensure_ascii=False, indent=2))
                
                # Graph 검색 결과
                print(f"\n🔍 Graph 검색 결과: {len(result['graph_results'])}개")
                if result["graph_results"]:
                    for j, res in enumerate(result["graph_results"][:3], 1):
                        print(f"  {j}. {res.get('entity', res.get('id', 'N/A'))}")
                
                # Vector 검색 결과
                print(f"\n🔍 Vector 검색 결과: {len(result['vector_results'])}개")
                if result["vector_results"]:
                    for j, res in enumerate(result["vector_results"][:3], 1):
                        similarity = res.get("similarity", 0.0)
                        print(f"  {j}. {res.get('entity', res.get('node_id', 'N/A'))} (유사도: {similarity:.3f})")
                
                # 통합 결과
                print(f"\n🔗 통합 결과: {len(result['merged_results'])}개")
                if result["merged_results"]:
                    for j, res in enumerate(result["merged_results"][:3], 1):
                        final_score = res.get("final_score", 0.0)
                        print(f"  {j}. {res.get('entity', res.get('node_id', 'N/A'))} (점수: {final_score:.3f})")
                
                # 답변 출력 (이미 QueryEngine에서 생성됨)
                if result.get("answer"):
                    print("\n📝 생성된 답변:")
                    print("-" * 80)
                    print(result["answer"])
                    print("-" * 80)
                elif answer_generator:
                    print("\n💬 답변 생성 중...")
                    try:
                        answer = answer_generator.generate_answer(
                            query=query,
                            results=result["merged_results"],
                            intent=result["intent"],
                            max_results=3
                        )
                        
                        print("\n📝 생성된 답변:")
                        print("-" * 80)
                        print(answer)
                        print("-" * 80)
                    except Exception as e:
                        logger.error(f"답변 생성 실패: {e}")
                        print(f"\n❌ 답변 생성 실패: {e}")
                else:
                    print("\n⚠️  답변 생성 기능이 비활성화되어 있습니다.")
                
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
    test_query_engine()

