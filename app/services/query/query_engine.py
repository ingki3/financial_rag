"""
Query Engine Service

질의 응답 시스템의 메인 엔진
Phase 8: 질의 응답 시스템

Intent 추출 → Graph 검색 → Vector 검색 → 결과 통합 → 답변 생성
"""

import logging
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv

from app.services.query.intent_extractor import IntentExtractor
from app.services.query.cypher_query_builder import CypherQueryBuilder
from app.services.graph.graph_loader import GraphLoader
from app.services.query.vector_search import VectorSearch
from app.services.query.answer_generator import AnswerGenerator

load_dotenv()

logger = logging.getLogger(__name__)


class QueryEngine:
    """질의 응답 엔진"""
    
    def __init__(
        self,
        graph_loader: Optional[GraphLoader] = None,
        intent_extractor: Optional[IntentExtractor] = None,
        answer_generator: Optional[AnswerGenerator] = None,
        graph_name: str = "financial_kg"
    ):
        self._original_query = None  # 원본 질의 저장
        """
        QueryEngine 초기화
        
        Args:
            graph_loader: GraphLoader 인스턴스 (None이면 자동 생성)
            intent_extractor: IntentExtractor 인스턴스 (None이면 자동 생성)
            answer_generator: AnswerGenerator 인스턴스 (None이면 자동 생성)
            graph_name: 그래프 이름
        """
        # GraphLoader 초기화
        if graph_loader:
            self.graph_loader = graph_loader
        else:
            self.graph_loader = GraphLoader(graph_name=graph_name)
            self.graph_loader.connect()
        
        # IntentExtractor 초기화
        if intent_extractor:
            self.intent_extractor = intent_extractor
        else:
            self.intent_extractor = IntentExtractor()
        
        # CypherQueryBuilder 초기화
        self.query_builder = CypherQueryBuilder()
        
        # VectorSearch 초기화
        self.vector_search = VectorSearch(self.graph_loader)
        
        # AnswerGenerator 초기화
        if answer_generator:
            self.answer_generator = answer_generator
        else:
            try:
                self.answer_generator = AnswerGenerator()
            except Exception as e:
                logger.warning(f"AnswerGenerator 초기화 실패: {e}. 답변 생성 기능이 비활성화됩니다.")
                self.answer_generator = None
    
    def extract_intent(self, query: str) -> Dict:
        """
        질의에서 Intent 추출
        
        Args:
            query: 사용자 질의
            
        Returns:
            Intent 딕셔너리
        """
        self._original_query = query  # 원본 질의 저장
        return self.intent_extractor.extract_intent_sync(query)
    
    def graph_search(self, intent: Dict) -> List[Dict]:
        """
        Graph 기반 검색
        
        Args:
            intent: Intent 객체
            
        Returns:
            검색 결과 리스트
        """
        try:
            # Cypher 쿼리 생성
            cypher_query, params = self.query_builder.build_query(intent)
            
            logger.debug(f"Cypher query: {cypher_query}")
            logger.debug(f"Params: {params}")
            
            # 쿼리 실행
            results = self.graph_loader.execute_query(cypher_query, params)
            
            logger.info(f"Graph search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return []
    
    def _vector_search(
        self, 
        intent: Dict, 
        top_k: int = 10,
        similarity_threshold: float = 0.5  # 기본값을 0.5로 낮춰서 더 많은 결과 반환
    ) -> List[Dict]:
        """
        Vector 기반 검색 (내부 메서드)
        
        Intent 분석 결과를 기반으로 Vector 검색을 수행합니다.
        
        Args:
            intent: Intent 객체
            top_k: 반환할 결과 수
            similarity_threshold: 최소 유사도 임계값
            
        Returns:
            검색 결과 리스트
        """
        try:
            # Intent 기반으로 검색 쿼리 텍스트 구성
            # 1. 원본 질의를 기본으로 사용
            query_text = self._original_query or ""
            
            # 2. Intent 정보를 기반으로 검색 쿼리 개선
            # target_entity_type과 filters 정보를 활용하여 더 정확한 검색
            target_type = intent.get("target_entity_type")
            filters = intent.get("filters", {})
            
            # Intent 기반 검색 쿼리 구성
            # 예: "애플의 기회 요소" -> "Apple opportunity" 또는 원본 질의 유지
            # 현재는 원본 질의를 그대로 사용하되, target_type으로 필터링
            
            if not query_text:
                logger.warning("No query text available for vector search")
                return []
            
            # Target 노드 타입 추출 (Intent에서)
            # target_entity_type을 사용하여 특정 노드 타입만 검색
            target_node_type = target_type
            
            # Vector 검색 수행 (Intent 기반)
            results = self.vector_search.search(
                query_text=query_text,
                target_node_type=target_node_type,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            logger.info(f"Vector search (intent-based) returned {len(results)} results")
            logger.debug(f"Intent used: target={target_type}, filters={filters}")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def merge_results(
        self, 
        graph_results: List[Dict], 
        vector_results: List[Dict],
        graph_weight: float = 0.6,
        vector_weight: float = 0.4
    ) -> List[Dict]:
        """
        Graph 검색과 Vector 검색 결과 통합 (RRF 기반)
        
        Args:
            graph_results: Graph 검색 결과
            vector_results: Vector 검색 결과
            graph_weight: Graph 검색 가중치
            vector_weight: Vector 검색 가중치
            
        Returns:
            통합된 결과 리스트
        """
        # RRF (Reciprocal Rank Fusion) 점수 계산
        merged = {}
        
        # Graph 결과에 점수 부여
        for rank, result in enumerate(graph_results, 1):
            # Graph 검색 결과는 "target.id" 키를 사용할 수 있음
            node_id = result.get("id") or result.get("node_id") or result.get("target.id")
            if not node_id:
                continue
            
            # Graph 결과를 표준화된 형식으로 변환
            normalized_result = {
                **result,
                "node_id": node_id,  # node_id로 통일
                "id": node_id,  # id도 설정
            }
            # target.* 키를 일반 키로 변환
            if "target.id" in normalized_result:
                normalized_result["node_id"] = normalized_result["target.id"]
                normalized_result["id"] = normalized_result["target.id"]
            if "target.entity" in normalized_result:
                normalized_result["entity"] = normalized_result["target.entity"]
            if "target.description" in normalized_result:
                normalized_result["description"] = normalized_result["target.description"]
            
            if node_id not in merged:
                merged[node_id] = {
                    **normalized_result,
                    "graph_rank": rank,
                    "vector_rank": None,
                    "graph_score": graph_weight / (60 + rank),  # RRF 점수
                    "vector_score": 0.0,
                    "final_score": 0.0
                }
            else:
                merged[node_id].update(normalized_result)
                merged[node_id]["graph_rank"] = rank
                merged[node_id]["graph_score"] = graph_weight / (60 + rank)
        
        # Vector 결과에 점수 부여
        for rank, result in enumerate(vector_results, 1):
            node_id = result.get("node_id")
            if not node_id:
                continue
            
            similarity = result.get("similarity", 0.0)
            
            if node_id not in merged:
                merged[node_id] = {
                    **result,
                    "graph_rank": None,
                    "vector_rank": rank,
                    "graph_score": 0.0,
                    "vector_score": vector_weight * similarity,  # 유사도 기반 점수
                    "final_score": 0.0
                }
            else:
                merged[node_id]["vector_rank"] = rank
                merged[node_id]["vector_score"] = vector_weight * similarity
        
        # 최종 점수 계산
        for node_id, result in merged.items():
            result["final_score"] = result["graph_score"] + result["vector_score"]
        
        # 최종 점수 순으로 정렬
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x["final_score"], reverse=True)
        
        logger.info(f"Merged {len(merged_list)} unique results")
        return merged_list
    
    def query(
        self, 
        user_query: str,
        top_k: int = 10,
        use_vector_search: bool = False,
        use_graph_search: bool = True,
        generate_answer: bool = True
    ) -> Dict:
        """
        사용자 질의 처리 메인 함수
        
        Args:
            user_query: 사용자 질의
            top_k: 반환할 결과 수
            use_vector_search: Vector 검색 사용 여부
            use_graph_search: Graph 검색 사용 여부
            generate_answer: 답변 생성 여부
            
        Returns:
            {
                "intent": Intent 객체,
                "graph_results": Graph 검색 결과,
                "vector_results": Vector 검색 결과,
                "merged_results": 통합된 결과,
                "answer": 생성된 답변 (선택적)
            }
        """
        logger.info(f"Processing query: {user_query}")
        
        # 1. Intent 추출
        intent = self.extract_intent(user_query)
        logger.info(f"Extracted intent: {intent}")
        
        graph_results = []
        vector_results = []
        
        # 2. Graph 검색
        if use_graph_search:
            graph_results = self.graph_search(intent)
        
        # 3. Vector 검색
        if use_vector_search:
            vector_results = self._vector_search(intent, top_k=top_k)
        
        # 4. 결과 통합
        merged_results = []
        if graph_results or vector_results:
            merged_results = self.merge_results(graph_results, vector_results)
            # Top K로 제한
            merged_results = merged_results[:top_k]
        
        # 5. 답변 생성
        answer = None
        if generate_answer and self.answer_generator and merged_results:
            try:
                answer = self.answer_generator.generate_answer(
                    query=user_query,
                    results=merged_results,
                    intent=intent,
                    max_results=min(5, len(merged_results))
                )
            except Exception as e:
                logger.error(f"Failed to generate answer: {e}")
        
        return {
            "intent": intent,
            "graph_results": graph_results,
            "vector_results": vector_results,
            "merged_results": merged_results,
            "answer": answer,
            "query": user_query
        }
    
    def close(self):
        """리소스 정리"""
        if hasattr(self.graph_loader, 'close'):
            self.graph_loader.close()

