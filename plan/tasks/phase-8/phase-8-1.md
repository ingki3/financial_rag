# Phase 8.1: Intent 추출 구현

## 📋 개요

사용자 질의에서 의도를 추출하는 모듈을 구현합니다.

## 🎯 목표

- Gemini Structured Output 활용
- 질의 유형 분류
- 엔티티 추출 (기업, 제품, 인물 등)

## 📝 상세 구현

### Intent 구조

```python
{
    "query_type": "opportunities",
    "entities": {
        "companies": ["AAPL"],
        "products": ["iPhone 15"],
        "persons": []
    },
    "filters": {
        "time_range": "2024"
    }
}
```

### 프롬프트 관리

- YAML 파일: `app/prompts/intent_extractor.yaml`

## 📁 파일 위치

**파일**: `app/services/query/intent_extractor.py`

## 📝 History

