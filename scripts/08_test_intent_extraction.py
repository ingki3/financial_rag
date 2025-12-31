#!/usr/bin/env python
"""
Intent 추출 테스트 스크립트

두 가지 Gemini 모델로 동일한 질의에 대한 Intent 추출을 테스트합니다.
- gemini-3-flash-preview
- gemini-2.5-flash
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.intent_extractor import IntentExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 테스트 질의 목록
TEST_QUERIES = [
    # 기본 질의
    "애플에게 사업상 리스크 항목에 대해 설명해줘",
    "테슬라의 최근 기회 요소는?",
    "엔비디아의 AI 기술에 대해 알려줘",
    "구글의 2023년 주요 이벤트 목록 보여줘",
    "마이크로소프트의 Office 365 제품과 관련된 리스크는?",
    "애플의 iPhone 15가 언급된 기회 요소는?",
    "메타의 재무적 리스크를 분석해줘",
    "아마존의 경쟁적 위험 요소는 무엇인가?",
    "엔비디아와 애플의 AI 기술을 비교해줘",
    "테슬라의 최근 2년간 운영상 이벤트를 보여줘",
    
    # 복합 질의
    "애플의 2023년 사업상 리스크 중 iPhone과 관련된 것은?",
    "테슬라의 최근 3년간 재무적 기회와 리스크를 비교해줘",
    "구글의 Tim Cook이 언급된 기회 요소는?",
    "애플의 10-K 공시에서 추출된 리스크 요소는?",
    "마이크로소프트의 규제 관련 리스크를 설명해줘",
    "엔비디아의 제품군을 보여줘",
    "애플의 시장 확장 기회는?",
    
    # 영어 질의
    "What are Apple's business risks?",
    "Show me Tesla's recent opportunities",
    "Compare NVIDIA and Apple's AI technologies",
]


async def test_model(model_name: str, queries: List[str]) -> Dict:
    """특정 모델로 질의 테스트"""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing model: {model_name}")
    logger.info(f"{'='*80}")
    
    extractor = IntentExtractor(model=model_name)
    results = []
    total_time = 0
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n[{i}/{len(queries)}] Query: {query}")
        
        start_time = time.time()
        try:
            intent = await extractor.extract_intent(query)
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            result = {
                "query": query,
                "intent": intent,
                "elapsed_time": elapsed_time,
                "success": True
            }
            
            logger.info(f"  ✅ Success ({elapsed_time:.2f}s)")
            logger.info(f"  Entity Type: {intent.get('target_entity_type')}")
            logger.info(f"  Query Text: {intent.get('query_text')}")
            logger.info(f"  Company: {intent.get('filters', {}).get('company')}")
            logger.info(f"  Query Type: {intent.get('query_type')}")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            result = {
                "query": query,
                "intent": None,
                "elapsed_time": elapsed_time,
                "success": False,
                "error": str(e)
            }
            
            logger.error(f"  ❌ Failed ({elapsed_time:.2f}s): {e}")
        
        results.append(result)
        
        # API Rate Limit 방지를 위한 짧은 대기
        await asyncio.sleep(0.5)
    
    return {
        "model": model_name,
        "results": results,
        "total_time": total_time,
        "avg_time": total_time / len(queries),
        "success_count": sum(1 for r in results if r["success"]),
        "failure_count": sum(1 for r in results if not r["success"])
    }


async def main():
    """메인 함수"""
    logger.info("="*80)
    logger.info("Intent Extraction Test")
    logger.info("="*80)
    
    models = ["gemini-2.5-flash-lite"]
    
    all_results = {}
    
    for model in models:
        try:
            result = await test_model(model, TEST_QUERIES)
            all_results[model] = result
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Summary for {model}:")
            logger.info(f"  Total Time: {result['total_time']:.2f}s")
            logger.info(f"  Average Time: {result['avg_time']:.2f}s")
            logger.info(f"  Success: {result['success_count']}/{len(TEST_QUERIES)}")
            logger.info(f"  Failure: {result['failure_count']}/{len(TEST_QUERIES)}")
            logger.info(f"{'='*80}\n")
            
        except Exception as e:
            logger.error(f"Failed to test model {model}: {e}")
            all_results[model] = {
                "model": model,
                "error": str(e)
            }
    
    # 결과 저장
    output_dir = Path("test_result")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "intent_extraction_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ Results saved to: {output_file}")
    
    # 비교 요약 출력
    logger.info("\n" + "="*80)
    logger.info("Comparison Summary")
    logger.info("="*80)
    
    for model in models:
        if model in all_results and "error" not in all_results[model]:
            r = all_results[model]
            logger.info(f"\n{model}:")
            logger.info(f"  Average Time: {r['avg_time']:.2f}s")
            logger.info(f"  Success Rate: {r['success_count']}/{len(TEST_QUERIES)} ({r['success_count']/len(TEST_QUERIES)*100:.1f}%)")
    
    # 상세 결과 출력
    logger.info("\n" + "="*80)
    logger.info("Detailed Results")
    logger.info("="*80)
    
    for model in models:
        if model in all_results and "error" not in all_results[model]:
            logger.info(f"\n{model}:")
            for i, result in enumerate(all_results[model]["results"], 1):
                status = "✅" if result["success"] else "❌"
                logger.info(f"  {i}. {status} [{result['elapsed_time']:.2f}s] {result['query']}")
                if not result["success"]:
                    logger.info(f"     Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())

