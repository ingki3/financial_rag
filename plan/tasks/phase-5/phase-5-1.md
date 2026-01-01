# Phase 5.1: Company Node 생성

## 📋 개요

각 티커에 대해 Company 노드를 생성합니다.

## 🎯 목표

- 티커당 1개의 Company 노드 생성
- 필수 필드 설정
- 고유 ID 생성

## 📝 상세 구현

### Node 구조

```python
{
    "id": "AAPL",
    "node_type": "Company",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "description": "...",
    "node_style": "static"
}
```

### ID 생성 규칙

- ID: `{ticker}` (예: `AAPL`)
- 티커당 1개만 생성

## 📁 파일 위치

**파일**: `app/services/processing/graph_generator.py`

## 📝 History

