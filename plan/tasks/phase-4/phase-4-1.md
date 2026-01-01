# Phase 4.1: 추출기 모듈 구현

## 📋 Sub-task 개요

LLM을 활용하여 텍스트에서 Knowledge Triplet을 추출하는 모듈을 구현합니다. Gemini LLM API를 사용하여 구조화된 Triplet을 추출하고, 프롬프트 YAML 파일을 통해 추출 로직을 관리합니다.

### 파일 경로
**파일**: `app/services/processing/triplet_extractor.py`

### Phase 전체 목표 기여
- Phase 3에서 파싱된 텍스트에서 Knowledge Triplet 추출
- Phase 5의 Static Graph 생성을 위한 엔티티 정보 제공
- Phase 6의 Dynamic Graph 생성을 위한 동적 엔티티 정보 제공

### 입력 데이터
- **텍스트**: 파싱된 공시 섹션 텍스트
- **메타데이터**: 티커, 공시 유형, 섹션명, Accession Number

### 출력 데이터
- **ExtractedTriplets 객체**: 추출된 Triplet 데이터
  - `opportunities`: 기회 요소 리스트
  - `risks`: 리스크 요소 리스트
  - `events`: 주요 이벤트 리스트
  - `technologies`: 기술 관련 정보 리스트
  - `mentioned_products_global`: 언급된 제품 리스트
  - `mentioned_persons_global`: 언급된 인물 리스트

### Class 구조

#### Class: `TripletExtractor`
Gemini를 활용한 Knowledge Triplet 추출 클래스

##### 속성 (Attributes)
- `model` (str): Gemini 모델명 (기본값: "gemini-3-flash-preview")
- `max_chunk_size` (int): 최대 청크 크기 (기본값: 30000)
- `client`: Gemini 클라이언트 인스턴스

##### 함수 (Methods)

###### `__init__(self, model: str = "gemini-3-flash-preview", api_key: Optional[str] = None, max_chunk_size: int = 30000)`
- **목적**: TripletExtractor 인스턴스 초기화
- **Input 구조 및 내용**:
  - `model` (str, optional): Gemini 모델명
  - `api_key` (str, optional): Gemini API 키 (없으면 환경변수에서 로드)
  - `max_chunk_size` (int, optional): 최대 청크 크기
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. 모델명, 최대 청크 크기 설정
  2. Gemini 클라이언트 초기화

###### `extract(self, text: str, ticker: str, filing_type: str, section: str, accession_number: str = "") -> ExtractedTriplets`
- **목적**: 텍스트에서 Knowledge Triplets 추출
- **Input 구조 및 내용**:
  - `text` (str): 추출 대상 텍스트
  - `ticker` (str): 기업 티커
  - `filing_type` (str): 공시 유형 (10-K, 10-Q, 8-K)
  - `section` (str): 섹션명
  - `accession_number` (str, optional): SEC Accession Number
- **Output 형식 및 내용**:
  - `ExtractedTriplets`: 추출된 Triplet 객체
- **함수 내부 동작 방식**:
  1. 텍스트 청킹 (긴 텍스트 분할)
  2. 각 청크에 대해 LLM 호출
  3. 결과 병합 및 중복 제거
  4. ExtractedTriplets 객체 반환

###### `_chunk_text(self, text: str) -> List[str]`
- **목적**: 긴 텍스트를 청크로 분할
- **Input 구조 및 내용**:
  - `text` (str): 분할할 텍스트
- **Output 형식 및 내용**:
  - `List[str]`: 청크 리스트
- **함수 내부 동작 방식**:
  1. 텍스트 길이 확인
  2. 문단 단위로 분할
  3. 최대 청크 크기 내에서 청크 생성

###### `_extract_from_chunk(self, text: str, ticker: str, filing_type: str, section: str) -> Dict`
- **목적**: 단일 청크에서 추출
- **Input 구조 및 내용**:
  - `text` (str): 청크 텍스트
  - `ticker` (str): 티커 심볼
  - `filing_type` (str): 공시 유형
  - `section` (str): 섹션명
- **Output 형식 및 내용**:
  - `Dict`: 추출된 Triplet 딕셔너리
- **함수 내부 동작 방식**:
  1. 프롬프트 렌더링
  2. Gemini API 호출
  3. JSON 파싱 및 반환

##### 상속 관계
- 없음 (독립 클래스)

#### Class: `TripletExtractorBatch`
여러 공시에서 Triplets를 일괄 추출하는 클래스

##### 속성 (Attributes)
- `parsed_dir` (Path): 파싱된 파일 디렉토리
- `output_dir` (Path): 추출 결과 저장 디렉토리
- `extractor` (TripletExtractor): TripletExtractor 인스턴스
- `TICKERS` (List[str]): 대상 티커 목록 (클래스 변수)
- `FILING_TYPES` (List[str]): 공시 유형 목록 (클래스 변수)
- `TARGET_SECTIONS` (Dict): 공시 유형별 추출 대상 섹션 (클래스 변수)

##### 함수 (Methods)

###### `extract_all(self) -> List[ExtractedTriplets]`
- **목적**: 모든 파싱 파일에서 Triplets 추출
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `List[ExtractedTriplets]`: 추출된 Triplet 리스트
- **함수 내부 동작 방식**:
  1. 모든 티커와 공시 유형 순회
  2. 각 파싱 파일에 대해 추출 수행
  3. 결과 저장 및 반환

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **LLM 기반 추출**
   - Gemini LLM API를 통한 구조화된 추출
   - JSON 형식 응답 파싱

2. **텍스트 청킹**
   - 긴 텍스트를 청크로 분할
   - 문단 단위 분할로 의미 보존

3. **프롬프트 관리**
   - YAML 파일을 통한 프롬프트 관리
   - 버전 관리 및 업데이트 용이

4. **배치 처리**
   - 여러 공시 파일 일괄 추출
   - Rate limiting 지원

## 📊 데이터 구조

### 입력 데이터 구조
- **텍스트**: 파싱된 섹션 텍스트 (문자열)
- **메타데이터**: 티커, 공시 유형, 섹션명, Accession Number

### 출력 데이터 구조
- **ExtractedTriplets 객체**:
  ```python
  {
      "ticker": str,
      "filing_type": str,
      "accession_number": str,
      "section": str,
      "opportunities": List[Dict],
      "risks": List[Dict],
      "events": List[Dict],
      "technologies": List[Dict],
      "strategies": List[Dict],
      "financials": List[Dict],
      "mentioned_products_global": List[Dict],
      "mentioned_persons_global": List[Dict]
  }
  ```

### 추출 대상
- **Opportunities**: 기회 요소
- **Risks**: 리스크 요소
- **Events**: 주요 이벤트 (날짜 포함)
- **Technologies**: 기술 관련 정보
- **mentioned_products**: 언급된 제품
- **mentioned_persons**: 언급된 인물
- **mentioned_companies**: 언급된 기업

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/processing/triplet_extractor.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.processing.triplet_extractor import TripletExtractor

# 추출기 인스턴스 생성
extractor = TripletExtractor(model="gemini-3-flash-preview")

# 텍스트에서 Triplet 추출
triplets = extractor.extract(
    text=section_text,
    ticker="AAPL",
    filing_type="10-K",
    section="risk_factors",
    accession_number="0000320193-24-000077"
)

print(f"Extracted {len(triplets.risks)} risks")
print(f"Extracted {len(triplets.opportunities)} opportunities")
```

### 에러 핸들링
- LLM API 호출 실패: 예외 처리 및 빈 결과 반환
- JSON 파싱 실패: 예외 처리 및 로깅
- 텍스트가 너무 짧은 경우: 경고 및 빈 결과 반환

## 🔄 상세 알고리즘/프로세스

### 추출 프로세스
1. **텍스트 청킹**
   - 텍스트 길이 확인
   - 최대 청크 크기 초과 시 문단 단위로 분할

2. **청크별 추출**
   - 각 청크에 대해 프롬프트 렌더링
   - Gemini API 호출
   - JSON 응답 파싱

3. **결과 병합**
   - 모든 청크의 결과 병합
   - 중복 제거 (entity 기준)

4. **결과 반환**
   - ExtractedTriplets 객체 생성 및 반환

### 예외 처리
- LLM API 호출 실패: 예외 처리 및 빈 결과 반환
- JSON 파싱 실패: 예외 처리 및 로깅
- 텍스트가 너무 짧은 경우: 경고 및 빈 결과 반환

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (필수)

### 외부 라이브러리 의존성
- `google-genai`: Gemini LLM API 클라이언트

### 설정 파일
- `app/prompts/triplet_extractor.yaml`: 추출 프롬프트 템플릿

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_triplet_extractor():
    extractor = TripletExtractor()
    triplets = extractor.extract(
        text="Apple faces intense competition...",
        ticker="AAPL",
        filing_type="10-K",
        section="risk_factors"
    )
    
    assert triplets.ticker == "AAPL"
    assert len(triplets.risks) >= 0

def test_chunk_text():
    extractor = TripletExtractor(max_chunk_size=1000)
    chunks = extractor._chunk_text("very long text...")
    assert len(chunks) > 0
```

### 통합 테스트 시나리오
- 실제 공시 텍스트로 추출 테스트
- 배치 추출 테스트
- 다양한 공시 유형 추출 테스트

### 검증 방법
- 추출된 Triplet 수 확인
- Triplet 구조 확인
- 프롬프트 렌더링 확인

## ⚠️ 주의사항

- LLM API 비용 발생
- API 속도 제한 준수 (Rate limiting 필요)
- 배치 처리로 효율성 향상
- 프롬프트 품질이 추출 결과에 큰 영향
- JSON 파싱 실패 시 재시도 고려

## 📝 History
