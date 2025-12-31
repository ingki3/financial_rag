"""
Embedding Generator Service

Risk, Opportunity, Event, Technology 노드에 description_embedding 필드를 추가합니다.
Gemini text-embedding-004 모델을 사용합니다 (768차원).
"""

import os
import logging
from typing import List, Dict, Optional
import asyncio
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# Gemini API 설정
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Embedding generation will be skipped.")


def configure_genai(api_key: Optional[str] = None):
    """Gemini API 설정"""
    if not GENAI_AVAILABLE:
        return False
    
    # GOOGLE_API_KEY 또는 GEMINI_API_KEY 사용
    key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        logger.warning("GOOGLE_API_KEY or GEMINI_API_KEY not found. Embedding generation will be skipped.")
        return False
    
    genai.configure(api_key=key)
    return True


def get_embedding_text(node: Dict) -> str:
    """
    노드에서 embedding 대상 텍스트 추출
    
    Args:
        node: 노드 딕셔너리
        
    Returns:
        embedding 대상 텍스트
    """
    entity = node.get("entity", "")
    description = node.get("description", "")
    node_type = node.get("node_type", "")
    
    # Event 노드는 date 포함
    if node_type == "Event":
        metadata = node.get("metadata", {})
        date = metadata.get("date", "") or node.get("date", "")
        if date:
            return f"{entity} ({date}): {description}"
    
    return f"{entity}: {description}"


def generate_embedding_sync(text: str, model: str = "models/text-embedding-004") -> List[float]:
    """
    단일 텍스트 embedding 생성 (동기)
    
    Args:
        text: embedding 대상 텍스트
        model: embedding 모델 이름
        
    Returns:
        embedding 벡터 (768차원)
    """
    if not GENAI_AVAILABLE:
        return []
    
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return []


async def generate_embedding(text: str, model: str = "models/text-embedding-004") -> List[float]:
    """
    단일 텍스트 embedding 생성 (비동기)
    
    Args:
        text: embedding 대상 텍스트
        model: embedding 모델 이름
        
    Returns:
        embedding 벡터 (768차원)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_embedding_sync, text, model)


def generate_embeddings_batch_sync(
    texts: List[str], 
    batch_size: int = 100,
    model: str = "models/text-embedding-004"
) -> List[List[float]]:
    """
    배치 단위 embedding 생성 (동기)
    
    Args:
        texts: embedding 대상 텍스트 리스트
        batch_size: 배치 크기 (기본 100)
        model: embedding 모델 이름
        
    Returns:
        embedding 벡터 리스트
    """
    if not GENAI_AVAILABLE:
        return [[] for _ in texts]
    
    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        try:
            logger.info(f"Generating embeddings batch {batch_num}/{total_batches} ({len(batch)} texts)")
            result = genai.embed_content(
                model=model,
                content=batch,
                task_type="retrieval_document"
            )
            # 배치 결과는 리스트로 반환됨
            if isinstance(result['embedding'][0], list):
                embeddings.extend(result['embedding'])
            else:
                # 단일 결과인 경우
                embeddings.append(result['embedding'])
        except Exception as e:
            logger.error(f"Failed to generate embeddings for batch {batch_num}: {e}")
            # 실패한 배치는 빈 벡터로 채움
            embeddings.extend([[] for _ in batch])
    
    return embeddings


async def generate_embeddings_batch(
    texts: List[str], 
    batch_size: int = 100,
    model: str = "models/text-embedding-004"
) -> List[List[float]]:
    """
    배치 단위 embedding 생성 (비동기)
    
    Args:
        texts: embedding 대상 텍스트 리스트
        batch_size: 배치 크기 (기본 100)
        model: embedding 모델 이름
        
    Returns:
        embedding 벡터 리스트
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        generate_embeddings_batch_sync, 
        texts, 
        batch_size,
        model
    )


def add_embeddings_to_nodes_sync(nodes: List[Dict]) -> List[Dict]:
    """
    노드 리스트에 embedding 추가 (동기)
    
    Args:
        nodes: 노드 딕셔너리 리스트
        
    Returns:
        embedding이 추가된 노드 리스트
    """
    if not nodes:
        return nodes
    
    if not GENAI_AVAILABLE:
        logger.warning("Gemini API not available. Skipping embedding generation.")
        return nodes
    
    # API 설정 확인
    if not configure_genai():
        logger.warning("Gemini API not configured. Skipping embedding generation.")
        return nodes
    
    # 텍스트 추출
    texts = [get_embedding_text(node) for node in nodes]
    
    # 빈 텍스트 필터링 및 인덱스 추적
    valid_indices = []
    valid_texts = []
    for i, text in enumerate(texts):
        if text.strip() and text != ": ":
            valid_indices.append(i)
            valid_texts.append(text)
    
    if not valid_texts:
        logger.warning("No valid texts for embedding generation.")
        return nodes
    
    logger.info(f"Generating embeddings for {len(valid_texts)} nodes...")
    
    # Embedding 생성
    embeddings = generate_embeddings_batch_sync(valid_texts)
    
    # 노드에 embedding 추가
    embedding_idx = 0
    for i, node in enumerate(nodes):
        if i in valid_indices:
            if embedding_idx < len(embeddings) and embeddings[embedding_idx]:
                node["description_embedding"] = embeddings[embedding_idx]
            embedding_idx += 1
    
    logger.info(f"Embeddings added to {len(valid_texts)} nodes.")
    return nodes


async def add_embeddings_to_nodes(nodes: List[Dict]) -> List[Dict]:
    """
    노드 리스트에 embedding 추가 (비동기)
    
    Args:
        nodes: 노드 딕셔너리 리스트
        
    Returns:
        embedding이 추가된 노드 리스트
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, add_embeddings_to_nodes_sync, nodes)


def add_embeddings_to_graph(graph: Dict) -> Dict:
    """
    Dynamic Graph의 모든 대상 노드에 embedding 추가
    
    Args:
        graph: Dynamic Graph 딕셔너리
        
    Returns:
        embedding이 추가된 Dynamic Graph
    """
    target_node_types = ["Risk", "Opportunity", "Event", "Technology"]
    
    for node_type in target_node_types:
        nodes = graph.get("nodes", {}).get(node_type, [])
        if nodes:
            logger.info(f"Adding embeddings to {len(nodes)} {node_type} nodes...")
            graph["nodes"][node_type] = add_embeddings_to_nodes_sync(nodes)
    
    return graph

