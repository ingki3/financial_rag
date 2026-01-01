# Phase 7.2: Cypher 쿼리 패턴

## 📋 개요

FalkorDB에 노드 및 링크를 생성하기 위한 Cypher 쿼리 패턴을 정의합니다.

## 🎯 목표

- 노드 생성 쿼리 패턴
- 링크 생성 쿼리 패턴
- MERGE를 사용한 중복 방지

## 📝 상세 구현

### 노드 생성 (MERGE)

```cypher
MERGE (n:Company {id: $id})
SET n.ticker = $ticker, n.name = $name, n.sector = $sector
```

### 링크 생성 (MERGE)

```cypher
MATCH (a:Company {id: $from_id})
MATCH (b:Risk {id: $to_id})
MERGE (a)-[r:HAS_RISKS]->(b)
```

### 인덱스 생성

```cypher
CREATE INDEX FOR (n:Company) ON (n.id)
CREATE INDEX FOR (n:Company) ON (n.ticker)
```

## 📝 History

