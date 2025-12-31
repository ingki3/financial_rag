"""
Vector Search Service

Embedding 기반 유사도 검색 서비스
Phase 8: 질의 응답 시스템
"""

import logging
import os
from typing import Dict, List, Optional, Any
import numpy as np
from dotenv import load_dotenv

from app.services.graph.graph_loader import GraphLoader
from app.services.shared.embedding_generator import generate_embedding_sync

load_dotenv()

logger = logging.getLogger(__name__)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    코사인 유사도 계산
    
    Args:
        vec1: 첫 번째 벡터
        vec2: 두 번째 벡터
        
    Returns:
        코사인 유사도 (0.0 ~ 1.0)
    """
    vec1_array = np.array(vec1)
    vec2_array = np.array(vec2)
    
    dot_product = np.dot(vec1_array, vec2_array)
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


class VectorSearch:
    """Vector 기반 유사도 검색 클래스"""
    
    def __init__(self, graph_loader: GraphLoader):
        """
        Vector 검색 초기화
        
        Args:
            graph_loader: GraphLoader 인스턴스
        """
        self.graph_loader = graph_loader
    
    def search(
        self, 
        query_text: str, 
        target_node_type: Optional[str] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Vector 기반 유사도 검색
        
        Args:
            query_text: 검색할 텍스트
            target_node_type: 검색할 노드 타입 (None이면 모든 타입)
            top_k: 반환할 결과 수
            similarity_threshold: 최소 유사도 임계값
            
        Returns:
            검색 결과 리스트 (각 항목은 {node_id, node_type, entity, description, similarity})
        """
        # 1. Query 텍스트를 embedding으로 변환
        query_embedding = generate_embedding_sync(query_text)
        
        if not query_embedding:
            logger.warning("Failed to generate embedding for query")
            return []
        
        # 2. 해당 노드 타입의 모든 노드에서 embedding 가져오기
        if target_node_type:
            # 특정 노드 타입만 검색
            cypher_query = f"""
            MATCH (n:{target_node_type})
            WHERE n.description_embedding IS NOT NULL
            RETURN n.id AS node_id, 
                   labels(n)[0] AS node_type,
                   n.entity AS entity,
                   n.description AS description,
                   n.description_embedding AS embedding,
                   n.ticker AS ticker
            """
        else:
            # 모든 노드 타입 검색
            cypher_query = """
            MATCH (n)
            WHERE n.description_embedding IS NOT NULL
            RETURN n.id AS node_id,
                   labels(n)[0] AS node_type,
                   n.entity AS entity,
                   n.description AS description,
                   n.description_embedding AS embedding,
                   n.ticker AS ticker
            """
        
        try:
            nodes = self.graph_loader.execute_query(cypher_query)
        except Exception as e:
            logger.error(f"Failed to fetch nodes for vector search: {e}")
            return []
        
        # 3. 각 노드의 embedding과 query embedding의 유사도 계산
        similarities = []
        for node in nodes:
            node_embedding = node.get("embedding")
            if not node_embedding:
                continue
            
            # FalkorDB에서 배열로 저장된 embedding을 리스트로 변환
            if isinstance(node_embedding, (list, tuple)):
                embedding_list = list(node_embedding)
            else:
                continue
            
            # 유사도 계산
            similarity = cosine_similarity(query_embedding, embedding_list)
            
            if similarity >= similarity_threshold:
                similarities.append({
                    "node_id": node.get("node_id"),
                    "node_type": node.get("node_type"),
                    "entity": node.get("entity"),
                    "description": node.get("description"),
                    "ticker": node.get("ticker"),
                    "similarity": similarity
                })
        
        # 4. 유사도 순으로 정렬
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 5. Top K 반환
        return similarities[:top_k]
    
    def search_by_node_type(
        self,
        query_text: str,
        node_types: List[str],
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> Dict[str, List[Dict]]:
        """
        여러 노드 타입에 대해 Vector 검색 수행
        
        Args:
            query_text: 검색할 텍스트
            node_types: 검색할 노드 타입 리스트
            top_k: 각 타입별 반환할 결과 수
            similarity_threshold: 최소 유사도 임계값
            
        Returns:
            {node_type: [results]} 형태의 딕셔너리
        """
        results = {}
        
        for node_type in node_types:
            results[node_type] = self.search(
                query_text=query_text,
                target_node_type=node_type,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
        
        return results


