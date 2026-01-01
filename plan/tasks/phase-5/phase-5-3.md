# Phase 5.3: Person Node 생성

## 📋 개요

추출된 데이터에서 언급된 인물을 수집하여 Person 노드를 생성합니다.

## 🎯 목표

- `mentioned_persons` 수집
- 이름 정규화
- 중복 제거
- Person Node 생성

## 📝 상세 구현

### Node 구조

```python
{
    "id": "person_aapl_tim_cook",
    "node_type": "Person",
    "name": "Tim Cook",
    "description": "...",
    "node_style": "static"
}
```

### ID 생성 규칙

- ID: `person_{ticker}_{normalized_name}`
- 정규화: NormalizationService 사용

## 📁 파일 위치

**파일**: `app/services/processing/graph_generator.py`

## 📝 History

