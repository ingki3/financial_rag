# Phase 2.1: 다운로더 모듈 구현

## 📋 Sub-task 개요

SEC EDGAR API를 통해 공시 자료를 다운로드하는 모듈을 구현합니다. `sec-edgar-downloader` 라이브러리를 사용하여 10-K, 10-Q, 8-K 공시를 다운로드하고, 프로젝트의 디렉토리 구조로 정리합니다.

### 파일 경로
**파일**: `app/services/download/sec_downloader.py`

### Phase 전체 목표 기여
- SEC EDGAR API를 통한 공시 자료 다운로드
- Phase 3의 파싱 단계를 위한 원본 파일 제공
- 체계적인 폴더 구조로 파일 관리

### 입력 데이터
- **환경 변수**: `SEC_USER_AGENT` (SEC API 접근을 위한 User-Agent)
- **티커 목록**: 7개 테크 기업 (AAPL, AMZN, TSLA, GOOGL, MSFT, META, NVDA)
- **공시 유형**: 10-K, 10-Q, 8-K

### 출력 데이터
- **파일 경로**: `data/raw/{ticker}/{filing_type}/` 폴더 구조
- **파일 형식**: HTML, SGML
- **다운로드 통계**: 공시 유형별 다운로드 수

### Class 구조

#### Class: `SECFilingDownloader`
SEC EDGAR에서 10-K, 10-Q, 8-K 공시 자료를 다운로드하는 클래스

##### 속성 (Attributes)
- `data_dir` (Path): 다운로드 파일 저장 디렉토리
- `user_agent` (str): SEC API 접근을 위한 User-Agent
- `downloader` (Downloader): sec-edgar-downloader 인스턴스
- `TICKERS` (List[str]): 대상 티커 목록 (클래스 변수)
- `FILING_TYPES` (Dict[str, int]): 공시 유형별 다운로드 제한 (클래스 변수)

##### 함수 (Methods)

###### `__init__(self, data_dir: str = "./data/raw", user_agent: str = None)`
- **목적**: SECFilingDownloader 인스턴스 초기화
- **Input 구조 및 내용**:
  - `data_dir` (str, optional): 저장 디렉토리 (기본값: "./data/raw")
  - `user_agent` (str, optional): User-Agent 문자열 (기본값: "FinancialKG user@example.com")
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. 저장 디렉토리 Path 객체 생성
  2. User-Agent 파싱 (이메일 추출)
  3. sec-edgar-downloader 인스턴스 생성

###### `download_filing(self, ticker: str, filing_type: str, limit: int) -> int`
- **목적**: 특정 티커의 특정 유형 공시 다운로드
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `filing_type` (str): 공시 유형 ("10-K", "10-Q", "8-K")
  - `limit` (int): 다운로드 제한 수
- **Output 형식 및 내용**:
  - `int`: 다운로드된 파일 수
- **함수 내부 동작 방식**:
  1. sec-edgar-downloader로 다운로드
  2. 기본 저장 위치에서 프로젝트 디렉토리로 이동
  3. 다운로드 수 반환

###### `download_all_filings(self, ticker: str) -> Dict[str, int]`
- **목적**: 특정 티커의 모든 유형 공시 다운로드
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
- **Output 형식 및 내용**:
  - `Dict[str, int]`: 공시 유형별 다운로드 수
- **함수 내부 동작 방식**:
  1. 각 공시 유형별로 `download_filing` 호출
  2. API 속도 제한 준수 (1초 대기)
  3. 결과 딕셔너리 반환

###### `download_all(self) -> Dict[str, Dict[str, int]]`
- **목적**: 모든 대상 기업의 모든 공시 다운로드
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `Dict[str, Dict[str, int]]`: 기업별, 공시 유형별 다운로드 수
- **함수 내부 동작 방식**:
  1. 모든 티커에 대해 `download_all_filings` 호출
  2. 기업 간 간격 유지 (2초 대기)
  3. 전체 결과 반환

###### `get_downloaded_files(self, ticker: str, filing_type: str) -> List[Path]`
- **목적**: 다운로드된 파일 목록 반환
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `filing_type` (str): 공시 유형
- **Output 형식 및 내용**:
  - `List[Path]`: 다운로드된 파일 경로 리스트
- **함수 내부 동작 방식**:
  1. 해당 디렉토리에서 HTML/TXT 파일 검색
  2. 파일 경로 리스트 반환

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **SEC EDGAR API 연동**
   - sec-edgar-downloader 라이브러리 활용
   - User-Agent 설정

2. **공시 다운로드**
   - 10-K: 최근 3년
   - 10-Q: 최근 12분기 (3년)
   - 8-K: 최근 20건

3. **파일 관리**
   - 프로젝트 디렉토리 구조로 정리
   - 티커별, 공시 유형별 폴더 구조

4. **API 속도 제한 준수**
   - 초당 10건 이하
   - 요청 간 대기 시간 설정

## 📊 데이터 구조

### 입력 데이터 구조
- **환경 변수**: `SEC_USER_AGENT` (문자열)
- **티커 목록**: `["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]`
- **공시 유형 설정**:
  ```python
  {
      "10-K": 3,   # 최근 3년
      "10-Q": 12,  # 최근 12분기
      "8-K": 20    # 최근 20건
  }
  ```

### 출력 데이터 구조
- **폴더 구조**:
  ```
  data/raw/
    {ticker}/
      10-K/
        {accession_number}/
          {accession_number}.htm
          {accession_number}.txt
      10-Q/
        ...
      8-K/
        ...
  ```
- **다운로드 통계**:
  ```python
  {
      "AAPL": {
          "10-K": 3,
          "10-Q": 12,
          "8-K": 20
      }
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/download/sec_downloader.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.download.sec_downloader import SECFilingDownloader

# 다운로더 인스턴스 생성
downloader = SECFilingDownloader(
    data_dir="./data/raw",
    user_agent="FinancialKG user@example.com"
)

# 특정 티커의 모든 공시 다운로드
results = downloader.download_all_filings("AAPL")
print(results)  # {"10-K": 3, "10-Q": 12, "8-K": 20}

# 모든 기업의 모든 공시 다운로드
all_results = downloader.download_all()

# 다운로드된 파일 목록 조회
files = downloader.get_downloaded_files("AAPL", "10-K")
```

### 에러 핸들링
- 다운로드 실패: 로깅 및 0 반환
- 파일 이동 실패: 예외 처리 및 로깅
- API 속도 제한: 요청 간 대기 시간 설정

## 🔄 상세 알고리즘/프로세스

### 다운로드 프로세스
1. **초기화**
   - 저장 디렉토리 생성
   - sec-edgar-downloader 인스턴스 생성

2. **다운로드 실행**
   - sec-edgar-downloader로 다운로드 (임시 위치)
   - 기본 저장 위치: `sec-edgar-filings/{ticker}/{filing_type}/`

3. **파일 이동**
   - 프로젝트 디렉토리로 이동: `data/raw/{ticker}/{filing_type}/`
   - 각 공시는 accession number 폴더로 저장

4. **통계 수집**
   - 다운로드된 파일 수 카운트
   - 결과 딕셔너리 반환

### 예외 처리
- 다운로드 실패: 로깅 및 0 반환
- 파일 이동 실패: 예외 처리 및 로깅
- API 속도 제한: 요청 간 대기 시간 설정

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `SEC_USER_AGENT`: SEC API 접근을 위한 User-Agent (선택적)

### 외부 라이브러리 의존성
- `sec-edgar-downloader`: SEC EDGAR 공시 다운로드 라이브러리

### 설정 파일
- 없음 (코드 내 상수로 정의)

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_sec_downloader_initialization():
    downloader = SECFilingDownloader()
    assert downloader.data_dir == Path("./data/raw")
    assert downloader.user_agent is not None

def test_download_filing():
    downloader = SECFilingDownloader()
    count = downloader.download_filing("AAPL", "10-K", 1)
    assert count >= 0

def test_get_downloaded_files():
    downloader = SECFilingDownloader()
    files = downloader.get_downloaded_files("AAPL", "10-K")
    assert isinstance(files, list)
```

### 통합 테스트 시나리오
- 전체 다운로드 프로세스 테스트
- 파일 이동 및 폴더 구조 확인
- 다운로드 통계 정확성 확인

### 검증 방법
- 다운로드된 파일 존재 확인
- 폴더 구조 확인
- 파일 수 통계 확인

## 📝 History
