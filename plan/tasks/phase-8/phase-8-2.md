# Phase 8.2: Cypher 쿼리 빌더 구현

## 📋 개요

Intent를 기반으로 동적 Cypher 쿼리를 생성하는 모듈을 구현합니다.

## 🎯 목표

- Intent 기반 쿼리 생성
- 다양한 질의 유형 지원
- 최적화된 쿼리 생성

## 📝 상세 구현

### 쿼리 패턴 예시

```cypher
// 기회 요소 질의
MATCH (c:Company {ticker: $ticker})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
RETURN o

// 제품 관련 리스크
MATCH (p:Product {name: $product_name})-[:IS_MENTIONED_IN]->(r:Risk)
RETURN r
```

## 📁 파일 위치

**파일**: `app/services/query/cypher_query_builder.py`

## 📝 History

