# Phase 6.3: Embedding 생성

## 📋 개요

Risk, Opportunity, Event, Technology 노드에 의미 기반 검색을 위한 embedding을 추가합니다.

## 🎯 목표

- Gemini text-embedding-004 모델 사용
- 768차원 벡터 생성
- 배치 처리로 효율성 향상

## 📝 상세 구현

### Embedding 대상 노드

- Risk: `{entity}: {description}`
- Opportunity: `{entity}: {description}`
- Event: `{entity} ({date}): {description}`
- Technology: `{entity}: {description}`

### 배치 처리

```python
async def generate_embeddings_batch(
    texts: List[str],
    batch_size: int = 100
) -> List[List[float]]:
    """배치 단위 embedding 생성"""
```

### Node에 Embedding 추가

```python
{
    "id": "risk_aapl_intense_competition_2024",
    "node_type": "Risk",
    "description_embedding": [0.123, 0.456, ...]  # 768차원
}
```

## 📁 파일 위치

**파일**: `app/services/processing/embedding_generator.py`

## ⚠️ 주의사항

- API 호출량: ~1,569 노드 → ~19회 배치 호출
- API 비용 발생
- 배치 크기 조정 가능

## 📝 History

