# Phase 8: 질의 응답 시스템

## 📋 개요

Phase 8는 자연어 질의를 처리하여 그래프 기반 답변을 생성하는 시스템을 구현하는 단계입니다.

## 🎯 목표

- Intent 추출 (Gemini Structured Output)
- Cypher 쿼리 빌더
- Vector 검색 (하이브리드)
- 답변 생성 (스트리밍)
- REST API 구현

## 📥 입력 데이터 상세

### 데이터 소스
- **사용자 입력**: 자연어 질의 (텍스트)
- **FalkorDB**: 그래프 데이터베이스 (Phase 7에서 적재된 데이터)

### 데이터 형식
- **질의**: 문자열 (자연어)
- **FalkorDB**: 그래프 데이터베이스 (Cypher 쿼리로 접근)

### 데이터 구조
- **질의 예시**:
  - "What are the main risks for Apple?"
  - "Who are the key executives at Tesla?"
  - "What products does NVIDIA make?"

## 📤 출력 데이터 상세

### 출력 형식
- **API 응답**: JSON 형식
- **스트리밍**: 텍스트 스트림 (선택적)

### 데이터 구조
```json
{
  "answer": "Apple Inc. faces several key risks including...",
  "sources": [
    {
      "document_id": "doc_aapl_10k_2024",
      "section_id": "section_aapl_10k_2024_item1a",
      "title": "Risk Factors",
      "excerpt": "..."
    }
  ],
  "query_type": "risk_analysis",
  "confidence": 0.95
}
```

## 🔄 주요 작업 단계

1. **Intent 추출** (Phase 8.1)
   - Gemini Structured Output으로 질의 의도 파악
   - 질의 타입 분류

2. **Cypher 쿼리 빌더** (Phase 8.2)
   - Intent에 따라 Cypher 쿼리 생성
   - 그래프 탐색 쿼리 구성

3. **Vector 검색** (Phase 8.3)
   - Embedding 기반 유사도 검색
   - 하이브리드 검색 (Cypher + Vector)

4. **답변 생성** (Phase 8.4)
   - LLM을 통한 답변 생성
   - 스트리밍 지원

5. **API 엔드포인트 구현** (Phase 8.5)
   - REST API 구현
   - 요청/응답 처리

## 📊 사용하는 데이터 구조 및 스키마

- **Intent 구조**: 질의 타입, 파라미터
- **Cypher 쿼리**: 그래프 탐색 쿼리
- **Vector Embedding**: 의미 기반 검색
- **답변 구조**: 답변 텍스트, 출처 정보, 신뢰도

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 7**: Graph DB 저장 완료 필요
  - FalkorDB에 노드 및 링크 적재 완료
  - Embedding 데이터 저장 완료

### 다음 Phase로의 데이터 전달
- **Phase 9 (테스트 및 검증)**:
  - API 엔드포인트 테스트
  - 질의 응답 품질 검증

## 🔗 관련 문서

- `phase-8-1.md`: Intent 추출 구현 상세
- `phase-8-2.md`: Cypher 쿼리 빌더 구현 상세
- `phase-8-3.md`: Vector 검색 구현 상세
- `phase-8-4.md`: 답변 생성 구현 상세
- `phase-8-5.md`: API 엔드포인트 구현 상세

## 📝 History

