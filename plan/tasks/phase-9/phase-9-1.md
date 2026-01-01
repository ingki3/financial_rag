# Phase 9.1: 단위 테스트

## 📋 Sub-task 개요

각 모듈의 개별 기능을 검증하는 단위 테스트를 작성합니다. 다운로더, 파서, 추출기, Graph 생성 모듈 등 각 모듈의 기능을 독립적으로 테스트합니다.

### 파일 경로
**파일**: `tests/test_downloader.py`, `tests/test_parser.py`, `tests/test_extractor.py`, `tests/test_graph_generator.py` 등

### Phase 전체 목표 기여
- 각 모듈의 기능 검증
- 버그 조기 발견
- 코드 품질 향상

### 입력 데이터
- **테스트 데이터**: 실제 또는 모의 데이터
- **테스트 케이스**: 각 모듈의 기능별 테스트 케이스

### 출력 데이터
- **테스트 결과**: 성공/실패 여부 및 상세 로그

### Class 구조
**해당 없음** (테스트 파일)

## 🎯 주요 기능

1. **다운로더 모듈 테스트**
   - SEC EDGAR 다운로드 테스트
   - 파일 저장 테스트

2. **파서 모듈 테스트**
   - HTML/SGML 파싱 테스트
   - 섹션 추출 테스트

3. **추출기 모듈 테스트**
   - Triplet 추출 테스트
   - LLM 호출 테스트

4. **Graph 생성 모듈 테스트**
   - 노드 생성 테스트
   - 링크 생성 테스트
   - 정규화 테스트

## 📊 데이터 구조

### 테스트 파일 구조
- `tests/test_downloader.py`: 다운로더 모듈 테스트
- `tests/test_parser.py`: 파서 모듈 테스트
- `tests/test_extractor.py`: 추출기 모듈 테스트
- `tests/test_graph_generator.py`: Graph 생성 모듈 테스트

## 💻 코드 예시 및 전체 코드 구현

### 테스트 파일 예시
```python
import pytest
from app.services.download.sec_downloader import SECFilingDownloader

def test_downloader():
    """다운로더 모듈 테스트"""
    downloader = SECFilingDownloader(...)
    # 테스트 로직
    pass

def test_parser():
    """파서 모듈 테스트"""
    # 테스트 로직
    pass
```

### 테스트 실행
```bash
# 전체 테스트 실행
pytest tests/

# 특정 모듈 테스트
pytest tests/test_downloader.py

# 상세 출력
pytest tests/ -v
```

## 🔄 상세 알고리즘/프로세스

### 테스트 프로세스
1. **테스트 환경 설정**
   - 테스트 데이터 준비
   - 모의 객체 설정

2. **테스트 실행**
   - 각 테스트 케이스 실행
   - 결과 검증

3. **정리**
   - 테스트 데이터 정리
   - 리소스 해제

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 테스트 환경 변수

### 외부 라이브러리 의존성
- `pytest`: 테스트 프레임워크
- `pytest-asyncio`: 비동기 테스트 지원
- `pytest-mock`: 모의 객체 지원

### 설정 파일
- `pytest.ini`: pytest 설정 파일

## 🧪 테스트 케이스

### 테스트 시나리오
- 다운로더 모듈 테스트
- 파서 모듈 테스트
- 추출기 모듈 테스트
- Graph 생성 모듈 테스트

### 검증 방법
- 테스트 결과 확인
- 로그 확인
- 데이터 검증

## ⚠️ 주의사항

- 테스트 환경과 프로덕션 환경 분리
- 테스트 데이터 정리 중요
- 모의 객체 사용 시 실제 동작과 일치 확인

## 📝 History
