# Phase 7: Graphiti add_episode 오버라이딩 검토

## 📌 목적

Phase 7에서 생성된 구조화된 Graph 데이터 (`{TICKER}_static_graph.json`, `{TICKER}_dynamic_graph.json`)를 FalkorDB에 적재하는 방법을 검토합니다. 특히 Graphiti의 `add_episode` 함수를 오버라이딩하여 현재 추출된 graph 형식대로 저장하는 방법의 가능성을 분석합니다.

---

## 🔍 현재 상황 분석

### 1. 현재 Graph 데이터 구조

#### Static Graph (`{TICKER}_static_graph.json`)
```json
{
  "ticker": "AAPL",
  "generated_at": "2025-12-29T06:00:16.777657Z",
  "nodes": {
    "Company": [
      {
        "id": "AAPL",
        "node_type": "Company",
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "description": "...",
        "node_style": "static"
      }
    ],
    "Product": [...],
    "Person": [...]
  },
  "links": [
    {
      "from": "AAPL",
      "to": "product_aapl_iphone",
      "relationship_type": "MAKE"
    },
    ...
  ]
}
```

#### Dynamic Graph (`{TICKER}_dynamic_graph.json`)
```json
{
  "ticker": "AAPL",
  "generated_at": "2025-12-29T06:51:33.878393Z",
  "nodes": {
    "Document": [...],
    "Section": [...],
    "Risk": [
      {
        "id": "risk_aapl_foreign_exchange_rate_risk_2024",
        "node_type": "Risk",
        "ticker": "AAPL",
        "entity": "Foreign Exchange Rate Risk",
        "description": "...",
        "description_embedding": [0.0123, -0.0456, ...],  // 768차원
        "node_style": "dynamic",
        "metadata": {
          "source_section": "financial_statements",
          "filing_type": "10-Q",
          "accession_number": "0000320193-24-000006"
        }
      }
    ],
    "Opportunity": [...],
    "Event": [...],
    "Technology": [...]
  },
  "links": [
    {
      "from": "section_aapl_10k_2023_business",
      "to": "doc_aapl_10k_0000320193-23-000106",
      "relationship_type": "IS_INCLUDED",
      "metadata": {"section_order": 1}
    },
    {
      "from": "risk_aapl_intense_competition_2023",
      "to": "section_aapl_10k_2023_business",
      "relationship_type": "IS_EXTRACTED_FROM",
      "metadata": {"extraction_method": "llm_extraction"}
    },
    {
      "from": "AAPL",
      "to": "risk_aapl_intense_competition_2023",
      "relationship_type": "HAS_RISKS"
    },
    {
      "from": "product_aapl_iphone",
      "to": "opp_aapl_expansion_2023",
      "relationship_type": "IS_MENTIONED_IN",
      "mention_context": "mentioned as a market opportunity for expansion"
    }
  ]
}
```

### 2. Graphiti의 add_episode 동작 방식

#### 현재 구현 (`app/services/graphiti_manager.py`)

```python
async def add_episode(self, episode: EpisodeData) -> bool:
    """단일 Episode 추가"""
    await self.graphiti.add_episode(
        name=episode.name,
        episode_body=episode.body,  # 텍스트 입력
        source_description=episode.source,
        reference_time=episode.reference_time,
        group_id=episode.group_id,
    )
```

**동작 흐름:**
1. **텍스트 입력**: `episode_body`에 텍스트를 전달
2. **LLM 추출**: Graphiti 내부에서 LLM을 사용하여 엔티티와 관계를 추출
3. **자동 그래프 생성**: 추출된 엔티티를 노드로, 관계를 링크로 자동 생성
4. **Embedding 생성**: Graphiti의 embedder를 사용하여 자동으로 embedding 생성
5. **DB 저장**: FalkorDB에 노드와 링크 저장

**예시:**
```python
episode = EpisodeData(
    name="AAPL Risk: Foreign Exchange Rate Risk",
    body="Foreign Exchange Rate Risk: The company is exposed to fluctuations...",
    source="SEC 10-Q - AAPL (2024), Section: financial_statements",
    reference_time=datetime(2024, 12, 31),
    group_id="AAPL"
)
await manager.add_episode(episode)
```

#### Graphiti의 내부 스키마

Graphiti는 자체적인 노드/링크 스키마를 사용합니다:
- **노드 타입**: Graphiti가 자동으로 결정 (Entity, Concept 등)
- **링크 타입**: Graphiti가 자동으로 결정 (RELATED_TO, MENTIONS 등)
- **속성**: Graphiti가 자동으로 추출한 속성들

**문제점:**
- 현재 프로젝트의 커스텀 스키마 (Company, Product, Risk, Opportunity, Event, Technology 등)와 다름
- 현재 프로젝트의 커스텀 링크 타입 (HAS_RISKS, IS_MENTIONED_IN 등)과 다름
- 이미 구조화된 노드/링크를 다시 LLM으로 추출하는 것은 비효율적

---

## 🤔 오버라이딩 가능성 검토

### 방법 1: add_episode 오버라이딩

#### 장점
- Graphiti의 retry 로직, 에러 처리 등 기존 인프라 활용 가능
- Graphiti의 embedder를 활용하여 embedding 생성 가능

#### 단점
1. **스키마 불일치**
   - Graphiti는 텍스트를 받아서 자동으로 노드/링크를 생성
   - 현재 graph는 이미 구조화된 노드/링크를 가지고 있음
   - Graphiti의 내부 스키마와 현재 프로젝트의 커스텀 스키마가 다름

2. **중복 추출**
   - 이미 추출된 노드/링크를 다시 LLM으로 추출하는 것은 비효율적
   - API 비용 증가
   - 처리 시간 증가

3. **제어 불가**
   - Graphiti의 내부 로직을 완전히 제어하기 어려움
   - 커스텀 노드 타입, 링크 타입을 정확히 지정하기 어려움

4. **Embedding 중복**
   - Phase 6에서 이미 생성한 `description_embedding` (768차원)이 있음
   - Graphiti가 다시 embedding을 생성하면 중복

#### 구현 예시 (비추천)

```python
class GraphitiManager:
    async def add_structured_graph(self, static_graph: Dict, dynamic_graph: Dict):
        """구조화된 graph를 Graphiti를 통해 저장 (비추천)"""
        # 각 노드를 텍스트로 변환하여 add_episode 호출
        for risk in dynamic_graph["nodes"]["Risk"]:
            episode = EpisodeData(
                name=f"{risk['ticker']} Risk: {risk['entity']}",
                body=f"{risk['entity']}: {risk['description']}",
                source=risk["metadata"]["source_section"],
                reference_time=datetime.now(),
                group_id=risk["ticker"]
            )
            await self.add_episode(episode)  # LLM이 다시 추출함 (비효율)
```

**문제점:**
- 이미 구조화된 데이터를 텍스트로 변환 후 다시 추출
- 커스텀 스키마 유지 불가
- 링크 정보 손실 (IS_MENTIONED_IN의 mention_context 등)

---

### 방법 2: Graphiti의 graph_driver 직접 사용

#### 장점
- Graphiti의 연결 관리, 인덱스 생성 등 인프라 활용
- 커스텀 스키마 유지 가능
- 직접 Cypher 쿼리 실행 가능

#### 단점
- Graphiti의 add_episode 로직을 우회
- 직접 Cypher 쿼리 작성 필요

#### 구현 예시

```python
class GraphitiManager:
    async def load_structured_graph(self, static_graph: Dict, dynamic_graph: Dict):
        """구조화된 graph를 직접 저장"""
        # Graphiti의 graph_driver 직접 사용
        driver = self.graphiti.graph_driver
        
        # 노드 생성
        for node in static_graph["nodes"]["Company"]:
            query = f"""
            MERGE (n:Company {{id: '{node['id']}'}})
            SET n.ticker = '{node['ticker']}',
                n.name = '{node['name']}',
                ...
            """
            await driver.execute_query(query)
        
        # 링크 생성
        for link in static_graph["links"]:
            query = f"""
            MATCH (a {{id: '{link['from']}'}})
            MATCH (b {{id: '{link['to']}'}})
            MERGE (a)-[r:{link['relationship_type']}]->(b)
            """
            await driver.execute_query(query)
```

**문제점:**
- Graphiti의 graph_driver API가 공개되어 있는지 확인 필요
- 직접 Cypher 쿼리 작성 및 관리 필요

---

### 방법 3: 현재 구현 (GraphLoader) 사용 (권장)

#### 장점
1. **완전한 제어**
   - 커스텀 스키마 유지
   - 노드/링크 타입 정확히 지정
   - 속성 완전히 제어

2. **효율성**
   - 이미 구조화된 데이터를 그대로 사용
   - LLM 재추출 불필요
   - API 비용 절감

3. **명확성**
   - 코드가 명확하고 이해하기 쉬움
   - 디버깅 용이

4. **Embedding 활용**
   - Phase 6에서 생성한 `description_embedding` 직접 사용
   - 중복 생성 방지

#### 단점
- Graphiti의 retry 로직, 에러 처리 등을 직접 구현해야 함
- Graphiti의 embedder를 별도로 활용하기 어려움 (하지만 이미 embedding이 있으므로 문제 없음)

#### 현재 구현 (`app/services/graph_loader.py`)

```python
class GraphLoader:
    def __init__(self, host: str, port: int, graph_name: str):
        self._client = FalkorDB(host=host, port=port)
        self._graph = self._client.select_graph(graph_name)
    
    def create_node(self, node: Dict) -> bool:
        """노드 생성 (MERGE 사용)"""
        label = self.NODE_LABELS.get(node["node_type"])
        query = f"MERGE (n:{label} {{id: '{node['id']}'}}) SET ..."
        self._graph.query(query)
    
    def create_link(self, link: Dict) -> bool:
        """링크 생성 (MERGE 사용)"""
        query = f"""
        MATCH (a {{id: '{link['from']}'}})
        MATCH (b {{id: '{link['to']}'}})
        MERGE (a)-[r:{link['relationship_type']}]->(b)
        """
        self._graph.query(query)
```

---

## 📊 방법 비교

| 항목 | add_episode 오버라이딩 | graph_driver 직접 사용 | GraphLoader (현재) |
|------|----------------------|----------------------|-------------------|
| **스키마 제어** | ❌ Graphiti 스키마 사용 | ✅ 커스텀 스키마 가능 | ✅ 완전한 제어 |
| **효율성** | ❌ LLM 재추출 | ✅ 직접 저장 | ✅ 직접 저장 |
| **코드 복잡도** | ⚠️ 중간 | ⚠️ 중간 | ✅ 단순 |
| **에러 처리** | ✅ Graphiti 인프라 | ⚠️ 직접 구현 | ⚠️ 직접 구현 |
| **Embedding 활용** | ❌ 중복 생성 | ✅ 직접 저장 | ✅ 직접 저장 |
| **유지보수성** | ❌ Graphiti 의존 | ⚠️ 중간 | ✅ 독립적 |
| **권장도** | ❌ 비추천 | ⚠️ 가능하나 복잡 | ✅ **권장** |

---

## 🎯 결론 및 권장사항

### 결론

**Graphiti의 `add_episode` 함수를 오버라이딩하여 현재 추출된 graph 형식대로 저장하는 것은 가능하지만, 권장하지 않습니다.**

### 이유

1. **스키마 불일치**
   - Graphiti는 자체 스키마를 사용하며, 커스텀 노드/링크 타입을 정확히 지정하기 어려움
   - 현재 프로젝트의 스키마 (Company, Product, Risk, Opportunity, Event, Technology 등)와 Graphiti의 스키마가 다름

2. **비효율성**
   - 이미 구조화된 노드/링크를 텍스트로 변환 후 다시 LLM으로 추출하는 것은 비효율적
   - API 비용 증가, 처리 시간 증가

3. **데이터 손실**
   - 링크의 `mention_context`, `metadata` 등 상세 정보가 손실될 수 있음
   - Phase 6에서 생성한 `description_embedding`을 활용할 수 없음

### 권장사항

**현재 구현한 `GraphLoader`를 사용하는 것을 권장합니다.**

#### 이유

1. **완전한 제어**
   - 커스텀 스키마를 정확히 유지
   - 노드/링크 타입, 속성을 완전히 제어

2. **효율성**
   - 이미 구조화된 데이터를 그대로 사용
   - LLM 재추출 불필요
   - Phase 6에서 생성한 embedding 직접 활용

3. **명확성**
   - 코드가 명확하고 이해하기 쉬움
   - 디버깅 및 유지보수 용이

4. **독립성**
   - Graphiti에 의존하지 않음
   - 향후 다른 Graph DB로 전환 시에도 유연함

### 대안: Graphiti와의 통합 (선택사항)

만약 Graphiti의 검색 기능을 활용하고 싶다면:

1. **현재 방식 유지**: `GraphLoader`로 구조화된 graph 저장
2. **Graphiti 병행 사용**: 검색 기능만 Graphiti 사용
   - 별도의 Graphiti 인스턴스로 검색 전용 데이터 저장
   - 또는 현재 graph를 Graphiti 형식으로 변환하여 검색 인덱스로 사용

---

## 📝 구현 체크리스트

### 현재 구현 (GraphLoader) ✅

- [x] `app/services/graph_loader.py` 구현 완료
- [x] `scripts/07_load_graph_to_db.py` 구현 완료
- [x] Static Graph 적재 로직
- [x] Dynamic Graph 적재 로직
- [x] Embedding 저장 로직
- [x] 인덱스 생성 로직
- [x] 에러 처리 및 통계

### Graphiti 통합 (선택사항)

- [ ] Graphiti 검색 기능 활용 방안 검토
- [ ] 현재 graph를 Graphiti 형식으로 변환하는 유틸리티
- [ ] 검색 전용 Graphiti 인스턴스 구성

---

## 🔗 관련 문서

- `docs/phase7_graph_db_storage_plan.md` - Phase 7 실행 계획
- `docs/graph_ontology_design.md` - Graph 스키마 정의
- `app/services/graph_loader.py` - GraphLoader 구현
- `app/services/graphiti_manager.py` - GraphitiManager 구현

---

## 📅 검토 일자

2025-12-29

