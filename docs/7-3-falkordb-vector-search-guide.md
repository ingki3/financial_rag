# FalkorDB Embedding Vector Search 가이드

## 📌 개요

FalkorDB에서 노드의 속성값을 embedding하여 vector search를 수행하는 방법을 설명합니다.

## 🔄 동작 원리

### 1. Graphiti를 통한 자동 처리 (현재 프로젝트 방식)

Graphiti는 노드를 추가할 때 자동으로:
1. 노드의 텍스트 속성을 embedding으로 변환
2. FalkorDB에 embedding 벡터를 저장
3. Vector 인덱스를 생성
4. 검색 시 자동으로 vector similarity search 수행

**현재 코드에서의 동작:**

```python
# app/services/graphiti_manager.py
await self.graphiti.add_episode(
    name=episode.name,
    episode_body=episode.body,  # 이 텍스트가 자동으로 embedding됨
    source_description=episode.source,
    reference_time=episode.reference_time,
    group_id=episode.group_id,
)

# 검색 시 자동으로 vector search 수행
results = await self.graphiti.search(
    query="애플의 기회 요소는?",  # 이 쿼리도 embedding되어 유사 노드 검색
    group_ids=["AAPL"],
    num_results=10
)
```

### 2. FalkorDB 직접 쿼리 방식 (수동 제어)

특정 노드의 속성값만 embedding하고, 직접 vector search를 수행하려면:

## 🛠 구현 방법

### 방법 1: Graphiti의 embedder를 활용한 직접 구현

```python
from app.services.graphiti_manager import GraphitiManager
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
import os

async def vector_search_by_node_property(
    manager: GraphitiManager,
    node_id: str,
    property_name: str,
    search_query: str,
    num_results: int = 10
):
    """
    특정 노드의 속성값을 embedding한 후, 
    그 벡터를 기준으로 유사한 노드를 검색
    
    Args:
        manager: GraphitiManager 인스턴스
        node_id: 기준이 되는 노드 ID
        property_name: embedding할 속성명 (예: "description", "entity")
        search_query: 검색할 쿼리 텍스트
        num_results: 반환할 결과 수
    """
    # 1. Graphiti의 embedder 가져오기
    embedder = manager.graphiti.embedder
    
    # 2. 특정 노드의 속성값 가져오기
    from falkordb import FalkorDB
    db = FalkorDB(host=manager.host, port=manager.port)
    graph = db.select_graph(manager.database)
    
    # 노드 조회
    result = graph.query(
        "MATCH (n) WHERE id(n) = $node_id RETURN n",
        {"node_id": node_id}
    )
    
    if not result.result_set:
        raise ValueError(f"Node {node_id} not found")
    
    node = result.result_set[0][0]
    property_value = node.properties.get(property_name)
    
    if not property_value:
        raise ValueError(f"Property {property_name} not found in node")
    
    # 3. 속성값을 embedding
    reference_embedding = await embedder.embed(property_value)
    
    # 4. 검색 쿼리도 embedding
    query_embedding = await embedder.embed(search_query)
    
    # 5. Vector similarity search (FalkorDB 직접 쿼리)
    # FalkorDB는 벡터 유사도 검색을 위해 코사인 유사도를 계산
    similarity_query = """
    MATCH (n)
    WHERE n.embedding IS NOT NULL
    WITH n, 
         cosine_similarity(n.embedding, $query_vector) AS similarity
    WHERE similarity > 0.7
    RETURN n, similarity
    ORDER BY similarity DESC
    LIMIT $limit
    """
    
    result = graph.query(
        similarity_query,
        {
            "query_vector": query_embedding,
            "limit": num_results
        }
    )
    
    return result.result_set
```

### 방법 2: Graphiti의 내부 메서드 활용

Graphiti는 내부적으로 vector search를 수행하므로, 이를 활용:

```python
async def find_similar_nodes_by_property(
    manager: GraphitiManager,
    reference_text: str,
    node_type: str = None,
    group_id: str = None,
    num_results: int = 10
):
    """
    특정 텍스트와 유사한 노드를 vector search로 찾기
    
    Args:
        manager: GraphitiManager 인스턴스
        reference_text: 기준 텍스트 (이것을 embedding하여 검색)
        node_type: 필터링할 노드 타입 (예: "Risk", "Opportunity")
        group_id: 필터링할 group_id (예: "AAPL")
        num_results: 반환할 결과 수
    """
    # Graphiti의 search 메서드는 자동으로:
    # 1. reference_text를 embedding
    # 2. 저장된 노드들의 embedding과 비교
    # 3. 유사도가 높은 노드 반환
    
    results = await manager.search(
        query=reference_text,
        group_ids=[group_id] if group_id else None,
        num_results=num_results
    )
    
    # 결과 필터링 (node_type이 있는 경우)
    if node_type:
        filtered_results = [
            r for r in results 
            if hasattr(r, 'node_type') and r.node_type == node_type
        ]
        return filtered_results
    
    return results
```

### 방법 3: FalkorDB 직접 쿼리 (최대 제어)

```python
from falkordb import FalkorDB
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
import numpy as np

async def direct_vector_search(
    host: str,
    port: int,
    database: str,
    reference_node_id: str,
    property_name: str,
    api_key: str,
    num_results: int = 10
):
    """
    FalkorDB에 직접 연결하여 vector search 수행
    
    Args:
        host: FalkorDB 호스트
        port: FalkorDB 포트
        database: 데이터베이스 이름
        reference_node_id: 기준 노드 ID
        property_name: embedding할 속성명
        api_key: Gemini API 키
        num_results: 반환할 결과 수
    """
    # 1. FalkorDB 연결
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(database)
    
    # 2. 기준 노드의 속성값 가져오기
    result = graph.query(
        "MATCH (n) WHERE id(n) = $node_id RETURN n",
        {"node_id": reference_node_id}
    )
    
    if not result.result_set:
        raise ValueError(f"Node {reference_node_id} not found")
    
    node = result.result_set[0][0]
    property_value = node.properties.get(property_name)
    
    if not property_value:
        raise ValueError(f"Property {property_name} not found")
    
    # 3. Embedding 생성
    embedder_config = GeminiEmbedderConfig(
        api_key=api_key,
        embedding_model="embedding-001"
    )
    embedder = GeminiEmbedder(config=embedder_config)
    
    reference_embedding = await embedder.embed(property_value)
    
    # 4. 모든 노드의 embedding과 비교
    # FalkorDB는 벡터를 배열로 저장하므로, 코사인 유사도를 직접 계산
    all_nodes_query = """
    MATCH (n)
    WHERE n.embedding IS NOT NULL
    RETURN id(n) AS node_id, n.embedding AS embedding, n
    """
    
    result = graph.query(all_nodes_query)
    
    # 5. 코사인 유사도 계산
    similarities = []
    for row in result.result_set:
        node_id = row[0]
        node_embedding = row[1]
        node_obj = row[2]
        
        # 코사인 유사도 계산
        similarity = cosine_similarity(reference_embedding, node_embedding)
        similarities.append({
            "node_id": node_id,
            "node": node_obj,
            "similarity": similarity
        })
    
    # 6. 유사도 순으로 정렬
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    
    return similarities[:num_results]


def cosine_similarity(vec1: list, vec2: list) -> float:
    """코사인 유사도 계산"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)
```

## 📝 실제 사용 예제

### 예제 1: 특정 Risk 노드와 유사한 Risk 찾기

```python
import asyncio
from app.services.graphiti_manager import GraphitiManager
import os
from dotenv import load_dotenv

load_dotenv()

async def find_similar_risks():
    """특정 Risk 노드의 description과 유사한 Risk 노드 찾기"""
    
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    await manager.initialize()
    
    try:
        # 1. 기준이 될 Risk 노드 찾기 (예: "Intense Competition")
        # Graphiti search로 먼저 찾기
        reference_risks = await manager.search(
            query="Intense Competition risk",
            group_ids=["AAPL"],
            num_results=1
        )
        
        if not reference_risks:
            print("기준 Risk 노드를 찾을 수 없습니다.")
            return
        
        reference_risk = reference_risks[0]
        print(f"기준 Risk: {reference_risk}")
        
        # 2. 이 Risk의 description을 기준으로 유사한 Risk 찾기
        # Graphiti는 자동으로 embedding하여 검색하므로,
        # description 텍스트를 그대로 검색 쿼리로 사용
        if hasattr(reference_risk, 'episode_body'):
            description = reference_risk.episode_body
        else:
            description = str(reference_risk)
        
        similar_risks = await manager.search(
            query=description,  # 이 텍스트를 embedding하여 유사 노드 검색
            group_ids=["AAPL"],
            num_results=10
        )
        
        print(f"\n유사한 Risk 노드 {len(similar_risks)}개 발견:")
        for i, risk in enumerate(similar_risks, 1):
            print(f"{i}. {risk}")
            
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(find_similar_risks())
```

### 예제 2: 특정 속성값으로 직접 검색

```python
async def search_by_custom_property():
    """특정 노드의 속성값을 embedding하여 검색"""
    
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    await manager.initialize()
    
    try:
        # 예: "supply chain"과 관련된 Risk 찾기
        search_text = "supply chain disruption risk"
        
        results = await manager.search(
            query=search_text,
            group_ids=["AAPL", "TSLA"],  # 여러 티커에서 검색
            num_results=20
        )
        
        print(f"'{search_text}'와 유사한 노드 {len(results)}개:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result}")
            
    finally:
        await manager.close()
```

### 예제 3: 찾은 노드에 대해 추가 쿼리 실행

```python
from falkordb import FalkorDB

async def vector_search_then_query():
    """Vector search로 노드를 찾은 후, 그 노드에 대해 그래프 쿼리 실행"""
    
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    await manager.initialize()
    
    try:
        # 1. Vector search로 노드 찾기
        search_query = "iPhone 15 product launch"
        results = await manager.search(
            query=search_query,
            group_ids=["AAPL"],
            num_results=5
        )
        
        if not results:
            print("검색 결과가 없습니다.")
            return
        
        # 2. 찾은 노드들의 ID 추출
        # Graphiti 결과에서 노드 정보 추출
        node_ids = []
        for result in results:
            # Graphiti 결과 구조에 따라 ID 추출 방법이 다를 수 있음
            if hasattr(result, 'id'):
                node_ids.append(result.id)
            elif hasattr(result, 'node_id'):
                node_ids.append(result.node_id)
        
        # 3. 찾은 노드들에 대해 그래프 쿼리 실행
        db = FalkorDB(host=manager.host, port=manager.port)
        graph = db.select_graph(manager.database)
        
        for node_id in node_ids:
            # 예: 해당 노드와 연결된 모든 노드 찾기
            query = """
            MATCH (n)-[r]->(connected)
            WHERE id(n) = $node_id
            RETURN type(r) AS relationship_type, 
                   labels(connected) AS connected_labels,
                   connected
            LIMIT 10
            """
            
            result = graph.query(query, {"node_id": node_id})
            
            print(f"\n노드 {node_id}와 연결된 노드들:")
            for row in result.result_set:
                rel_type = row[0]
                labels = row[1]
                connected = row[2]
                print(f"  - {rel_type} -> {labels}: {connected}")
                
    finally:
        await manager.close()
```

## 🔍 Graphiti의 내부 동작

Graphiti는 다음과 같이 동작합니다:

1. **노드 추가 시 (`add_episode`)**:
   - `episode_body` 텍스트를 `embedder.embed()`로 embedding
   - FalkorDB에 노드 생성 시 `embedding` 속성으로 벡터 저장
   - Vector 인덱스 자동 생성

2. **검색 시 (`search`)**:
   - 검색 쿼리 텍스트를 `embedder.embed()`로 embedding
   - 저장된 노드들의 `embedding` 속성과 코사인 유사도 계산
   - 유사도가 높은 순으로 정렬하여 반환
   - `cross_encoder`를 사용한 재랭킹 (선택적)

## 📌 주요 포인트

1. **Graphiti 사용 시**: 자동으로 embedding 생성 및 vector search 수행
2. **직접 제어 시**: `embedder`를 직접 사용하여 embedding 생성 후, FalkorDB 쿼리로 유사도 계산
3. **FalkorDB 벡터 저장**: 노드의 `embedding` 속성에 배열로 저장
4. **유사도 계산**: 코사인 유사도 사용 (FalkorDB 내장 함수 또는 직접 계산)

## 🚀 다음 단계

1. 특정 노드 타입만 필터링하는 검색 기능 추가
2. 여러 속성을 결합한 embedding (예: entity + description)
3. 하이브리드 검색 (Graph 구조 + Vector 유사도) 구현
4. 검색 결과 재랭킹 로직 개선

