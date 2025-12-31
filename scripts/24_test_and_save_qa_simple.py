#!/usr/bin/env python
"""
자연어 질의 테스트 및 간단한 결과 저장

질의/응답/소요 시간만 포함한 마크다운 파일 생성
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("자연어 질의 테스트 (질의/응답/소요 시간)")
    print("=" * 80)
    
    # 다양한 자연어 질의 테스트 케이스
    test_queries = [
        # 기본 질의
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 기술은?",
        
        # 설명 요청
        "구글의 AI 기술에 대해 알려줘",
        "애플의 사업상 리스크에 대해 설명해줘",
        "테슬라의 재무적 기회 요소를 분석해줘",
        
        # Product 필터
        "애플의 iPhone과 관련된 기회 요소는?",
        "애플의 Mac과 관련된 리스크는?",
        "테슬라의 Model 3와 관련된 이벤트는?",
        
        # Technology 필터
        "구글의 AI 기술과 관련된 기회 요소는?",
        "엔비디아의 GPU 기술은?",
        
        # 시간 필터
        "애플의 2023년 기회 요소는?",
        "테슬라의 최근 리스크는?",
        
        # 비교 질의
        "애플과 테슬라의 리스크를 비교해줘",
        "구글과 엔비디아의 기술을 비교해줘",
        
        # 복합 질의
        "애플의 2023년 iPhone과 관련된 기회 요소는?",
        "테슬라의 최근 Model 3와 관련된 이벤트는?",
    ]
    
    print(f"\n총 {len(test_queries)}개의 질의를 테스트합니다.\n")
    
    # QueryEngine 초기화
    print("QueryEngine 초기화 중...")
    engine = QueryEngine(graph_name="financial_kg")
    print("✅ 초기화 완료\n")
    
    results = []
    
    # 각 질의 테스트
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query}")
        
        total_start_time = time.time()
        timing = {}
        
        try:
            # 1. Intent 추출 시간 측정
            intent_start = time.time()
            intent = engine.extract_intent(query)
            timing["intent_extraction_ms"] = (time.time() - intent_start) * 1000
            
            # 2. Graph 검색 시간 측정
            graph_start = time.time()
            graph_results = engine.graph_search(intent)
            timing["graph_search_ms"] = (time.time() - graph_start) * 1000
            
            # 3. Vector 검색 비활성화
            vector_results = []
            timing["vector_search_ms"] = 0
            
            # 4. 결과 통합 시간 측정 (Graph 결과만 사용)
            merge_start = time.time()
            merged_results = engine.merge_results(graph_results, vector_results)
            merged_results = merged_results[:10]
            timing["merge_results_ms"] = (time.time() - merge_start) * 1000
            
            # 5. 답변 생성 시간 측정
            answer = None
            timing["answer_generation_ms"] = 0
            if engine.answer_generator and merged_results:
                answer_start = time.time()
                try:
                    answer = engine.answer_generator.generate_answer(
                        query=query,
                        results=merged_results,
                        intent=intent,
                        max_results=min(5, len(merged_results))
                    )
                    timing["answer_generation_ms"] = (time.time() - answer_start) * 1000
                except Exception as e:
                    print(f"  ⚠️ 답변 생성 실패: {e}")
            
            total_elapsed = (time.time() - total_start_time) * 1000
            
            result = {
                "query": query,
                "answer": answer or "답변 생성 실패",
                "time_ms": total_elapsed,
                "time_sec": total_elapsed / 1000,
                "timing": timing,
                "search_results": {
                    "graph_results_count": len(graph_results),
                    "vector_results_count": len(vector_results),
                    "merged_results_count": len(merged_results),
                    "top_results": [
                        {
                            "entity": r.get("entity") or r.get("description", "")[:100],
                            "description": r.get("description", "")[:200] if r.get("description") else None,
                            "node_type": r.get("node_type"),
                            "ticker": r.get("ticker"),
                            "score": r.get("final_score", 0.0)
                        }
                        for r in merged_results[:5]
                    ]
                }
            }
            results.append(result)
            
            print(f"  ✅ 완료 ({total_elapsed/1000:.2f}초)")
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            results.append({
                "query": query,
                "answer": f"오류 발생: {str(e)}",
                "time_ms": (time.time() - total_start_time) * 1000,
                "time_sec": (time.time() - total_start_time),
                "timing": timing
            })
    
    engine.close()
    
    # 마크다운 파일 생성
    output_file = Path("test_result/qa_simple_results.md")
    output_file.parent.mkdir(exist_ok=True)
    
    md_content = []
    md_content.append("# 자연어 질의 테스트 결과 (Graph 검색만)")
    md_content.append("")
    md_content.append(f"**테스트 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append(f"**총 질의 수**: {len(test_queries)}개")
    md_content.append(f"**검색 방식**: Graph 검색만 (Vector 검색 제외)")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    for i, result in enumerate(results, 1):
        query = result.get("query", "")
        answer = result.get("answer", "")
        time_sec = result.get("time_sec", 0)
        
        md_content.append(f"## {i}. {query}")
        md_content.append("")
        md_content.append(f"**소요 시간**: {time_sec:.2f}초")
        md_content.append("")
        md_content.append("**답변**:")
        md_content.append("")
        md_content.append(answer)
        md_content.append("")
        md_content.append("---")
        md_content.append("")
    
    # 통계 요약
    successful = [r for r in results if "오류" not in r.get("answer", "")]
    avg_time = sum([r.get("time_sec", 0) for r in successful]) / len(successful) if successful else 0
    
    md_content.append("## 통계 요약")
    md_content.append("")
    md_content.append(f"- **총 질의 수**: {len(test_queries)}개")
    md_content.append(f"- **성공**: {len(successful)}개")
    md_content.append(f"- **실패**: {len(results) - len(successful)}개")
    md_content.append(f"- **평균 소요 시간**: {avg_time:.2f}초")
    md_content.append("")
    
    # 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print("\n" + "=" * 80)
    print(f"✅ 테스트 완료")
    print(f"💾 결과 저장: {output_file}")
    print("=" * 80)
    
    # JSON 저장
    json_file = Path("test_result/qa_results.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(test_queries),
            "search_mode": "Graph only (Vector search excluded)",
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 JSON 저장: {json_file}")
    
    # JSON 출력 (표준 출력)
    print("\n" + "=" * 80)
    print("JSON 결과 출력")
    print("=" * 80)
    print(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(test_queries),
        "search_mode": "Graph only (Vector search excluded)",
        "results": results
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

