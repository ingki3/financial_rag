# Phase 3.1: 파서 모듈 구현

## 📋 Sub-task 개요

HTML/SGML 형식의 공시 파일을 파싱하여 주요 섹션을 추출하는 모듈을 구현합니다. BeautifulSoup을 사용하여 HTML을 파싱하고, 정규표현식을 통해 공시 유형별 주요 섹션을 추출합니다.

### 파일 경로
**파일**: `app/services/processing/filing_parser.py`

### Phase 전체 목표 기여
- Phase 2에서 다운로드한 원본 공시 파일을 파싱하여 구조화된 데이터로 변환
- Phase 4의 Knowledge Triplet 추출을 위한 텍스트 데이터 제공
- 공시 유형별 주요 섹션 추출

### 입력 데이터
- **파일 경로**: `data/raw/{ticker}/{filing_type}/{accession_number}/` 폴더의 HTML/SGML 파일
- **데이터 형식**: HTML, SGML

### 출력 데이터
- **ParsedFiling 객체**: 파싱된 공시 데이터
  - `metadata`: 공시 메타데이터
  - `sections`: 섹션별 텍스트 딕셔너리
  - `full_text`: 전체 텍스트

### Class 구조

#### Class: `FilingParser`
10-K, 10-Q, 8-K 파일에서 주요 섹션을 추출하는 클래스

##### 속성 (Attributes)
- `filing_dir` (Path): 공시 파일 디렉토리 경로
- `filing_type` (str): 공시 유형 ("10-K", "10-Q", "8-K")
- `ticker` (str): 티커 심볼
- `content` (str): 로드된 파일 내용
- `primary_file` (Path): 주요 파일 경로
- `SECTION_PATTERNS` (Dict): 공시 유형별 섹션 패턴 (클래스 변수)

##### 함수 (Methods)

###### `__init__(self, filing_dir: Path, filing_type: str, ticker: str)`
- **목적**: FilingParser 인스턴스 초기화
- **Input 구조 및 내용**:
  - `filing_dir` (Path): 공시 파일 디렉토리
  - `filing_type` (str): 공시 유형
  - `ticker` (str): 티커 심볼
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. 파일 디렉토리, 공시 유형, 티커 저장
  2. 주요 파일 경로 찾기

###### `load(self)`
- **목적**: HTML/SGML 파일 로드
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**: 없음
- **함수 내부 동작 방식**:
  1. 주요 파일 경로 찾기
  2. 파일 읽기 (utf-8, errors='ignore')
  3. BeautifulSoup으로 파싱
  4. 텍스트 추출

###### `extract_section(self, section_name: str) -> str`
- **목적**: 특정 섹션의 텍스트 추출
- **Input 구조 및 내용**:
  - `section_name` (str): 섹션 이름 (예: "business", "risk_factors")
- **Output 형식 및 내용**:
  - `str`: 섹션 텍스트 (없으면 빈 문자열)
- **함수 내부 동작 방식**:
  1. 섹션 패턴 조회
  2. 정규표현식으로 섹션 시작 위치 찾기
  3. 섹션 끝 위치 찾기
  4. 섹션 텍스트 추출 및 반환

###### `extract_all_sections(self) -> Dict[str, str]`
- **목적**: 현재 공시 유형의 모든 주요 섹션 추출
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `Dict[str, str]`: 섹션 이름과 텍스트 딕셔너리
- **함수 내부 동작 방식**:
  1. 공시 유형별 섹션 패턴 조회
  2. 각 섹션에 대해 `extract_section` 호출
  3. 결과 딕셔너리 반환

###### `parse(self) -> ParsedFiling`
- **목적**: 전체 파싱 수행
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `ParsedFiling`: 파싱된 공시 데이터 객체
- **함수 내부 동작 방식**:
  1. 파일 로드
  2. 모든 섹션 추출
  3. 메타데이터 생성
  4. ParsedFiling 객체 반환

##### 상속 관계
- 없음 (독립 클래스)

#### Class: `FilingParserBatch`
여러 공시를 일괄 파싱하는 클래스

##### 속성 (Attributes)
- `data_dir` (Path): 원본 데이터 디렉토리
- `TICKERS` (List[str]): 대상 티커 목록 (클래스 변수)
- `FILING_TYPES` (List[str]): 공시 유형 목록 (클래스 변수)

##### 함수 (Methods)

###### `parse_all(self) -> List[ParsedFiling]`
- **목적**: 모든 공시 파싱
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `List[ParsedFiling]`: 파싱된 공시 리스트
- **함수 내부 동작 방식**:
  1. 모든 티커와 공시 유형 순회
  2. 각 공시 디렉토리에 대해 FilingParser 생성
  3. 파싱 수행 및 결과 수집

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **HTML/SGML 파싱**
   - BeautifulSoup을 사용한 HTML 파싱
   - 텍스트 추출 및 정리

2. **섹션 추출**
   - 공시 유형별 섹션 패턴 정의
   - 정규표현식을 통한 섹션 위치 찾기
   - 섹션 텍스트 추출

3. **메타데이터 추출**
   - 티커, 공시 유형, Accession Number 추출
   - 파일 경로 및 텍스트 길이 정보

4. **일괄 처리**
   - 여러 공시 파일 일괄 파싱
   - 에러 처리 및 로깅

## 📊 데이터 구조

### 입력 데이터 구조
- **파일 경로**: `data/raw/{ticker}/{filing_type}/{accession_number}/`
- **파일 형식**: HTML, SGML

### 출력 데이터 구조
- **ParsedFiling 객체**:
  ```python
  {
      "metadata": {
          "ticker": str,
          "filing_type": str,
          "accession_number": str,
          "file_path": str,
          "text_length": int
      },
      "sections": {
          "business": str,
          "risk_factors": str,
          "mda": str
      },
      "full_text": str
  }
  ```

### 섹션 패턴 구조
```python
SECTION_PATTERNS = {
    "10-K": {
        "business": (start_pattern, end_pattern),
        "risk_factors": (start_pattern, end_pattern),
        "mda": (start_pattern, end_pattern)
    },
    "10-Q": {...},
    "8-K": {...}
}
```

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/processing/filing_parser.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.processing.filing_parser import FilingParser, FilingParserBatch
from pathlib import Path

# 단일 파일 파싱
filing_dir = Path("data/raw/AAPL/10-K/0000320193-24-000077")
parser = FilingParser(filing_dir, "10-K", "AAPL")
parsed = parser.parse()

print(f"Ticker: {parsed.metadata.ticker}")
print(f"Sections: {list(parsed.sections.keys())}")

# 일괄 파싱
batch = FilingParserBatch(data_dir="./data/raw")
results = batch.parse_all()
print(f"Parsed {len(results)} filings")
```

### 에러 핸들링
- 파일 읽기 실패: 예외 처리 및 로깅
- 섹션 추출 실패: 빈 문자열 반환
- 파싱 실패: 예외 처리 및 계속 진행

## 🔄 상세 알고리즘/프로세스

### 파싱 프로세스
1. **파일 로드**
   - 주요 파일 경로 찾기
   - 파일 읽기 (utf-8, errors='ignore')
   - BeautifulSoup으로 파싱

2. **섹션 추출**
   - 공시 유형별 섹션 패턴 조회
   - 정규표현식으로 섹션 시작 위치 찾기
   - 섹션 끝 위치 찾기
   - 섹션 텍스트 추출

3. **메타데이터 생성**
   - 티커, 공시 유형, Accession Number 추출
   - 파일 경로 및 텍스트 길이 정보

4. **결과 반환**
   - ParsedFiling 객체 생성 및 반환

### 예외 처리
- 파일 읽기 실패: 예외 처리 및 로깅
- 섹션 추출 실패: 빈 문자열 반환
- 파싱 실패: 예외 처리 및 계속 진행

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- `beautifulsoup4`: HTML 파싱
- `lxml`: XML/HTML 파서

### 설정 파일
- 없음 (코드 내 섹션 패턴 정의)

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_filing_parser():
    filing_dir = Path("data/raw/AAPL/10-K/0000320193-24-000077")
    parser = FilingParser(filing_dir, "10-K", "AAPL")
    parsed = parser.parse()
    
    assert parsed.metadata.ticker == "AAPL"
    assert parsed.metadata.filing_type == "10-K"
    assert len(parsed.sections) > 0

def test_extract_section():
    parser = FilingParser(...)
    parser.load()
    section_text = parser.extract_section("business")
    assert len(section_text) > 0
```

### 통합 테스트 시나리오
- 일괄 파싱 테스트
- 다양한 공시 유형 파싱 테스트
- 섹션 추출 정확도 확인

### 검증 방법
- 파싱된 섹션 수 확인
- 섹션 텍스트 길이 확인
- 메타데이터 정확성 확인

## ⚠️ 주의사항

- HTML 구조가 다양하여 섹션 추출이 불완전할 수 있음
- 파일 인코딩 처리 필요 (utf-8, errors='ignore')
- 대용량 파일 처리 시 메모리 고려
- 정규표현식 패턴이 모든 공시 형식에 맞지 않을 수 있음

## 📝 History
