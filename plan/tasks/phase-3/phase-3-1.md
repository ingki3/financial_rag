# Phase 3.1: 파서 모듈 구현

## 📋 개요

HTML/SGML 형식의 공시 파일을 파싱하여 주요 섹션을 추출하는 모듈을 구현합니다.

## 🎯 목표

- BeautifulSoup을 사용한 HTML 파싱
- 공시 유형별 섹션 패턴 정의
- 섹션별 텍스트 추출
- 메타데이터 추출

## 📝 상세 구현

### 클래스 구조

```python
class FilingParser:
    """10-K, 10-Q, 8-K 파일에서 주요 섹션을 추출하는 클래스"""
    
    SECTION_PATTERNS = {
        "10-K": {
            "business": r"item\s*1[.\s]*business",
            "risk_factors": r"item\s*1a[.\s]*risk\s*factors",
            "mda": r"item\s*7[.\s]*management",
        },
        "10-Q": {
            "mda": r"item\s*2[.\s]*management",
            "risk_factors": r"item\s*1a[.\s]*risk\s*factors",
        },
        "8-K": {
            "results_operations": r"item\s*2\.02",
            "other_events": r"item\s*8\.01",
        },
    }
```

### 주요 메서드

1. **`parse`**: 파일 파싱 및 섹션 추출
2. **`extract_section`**: 특정 섹션 텍스트 추출
3. **`get_metadata`**: 공시 메타데이터 추출

### 섹션 추출 프로세스

1. HTML 파일 로드
2. BeautifulSoup으로 파싱
3. 정규표현식으로 섹션 시작 위치 찾기
4. 섹션 텍스트 추출
5. JSON 형식으로 저장

## 📁 파일 위치

**파일**: `app/services/processing/filing_parser.py`

## ⚠️ 주의사항

- HTML 구조가 다양하여 섹션 추출이 불완전할 수 있음
- 파일 인코딩 처리 필요 (utf-8, errors='ignore')
- 대용량 파일 처리 시 메모리 고려

## 📝 History

