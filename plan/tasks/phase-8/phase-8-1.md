# Phase 8.1: Intent 추출 구현

## 📋 Sub-task 개요

사용자 질의에서 의도를 추출하는 모듈을 구현합니다. Gemini Structured Output을 활용하여 질의 유형을 분류하고, 엔티티(기업, 제품, 인물 등)를 추출합니다.

### 파일 경로
**파일**: `app/services/query/intent_extractor.py`

### Phase 전체 목표 기여
- 사용자 질의의 의도 파악
- 질의 유형 분류
- 엔티티 추출
- Phase 8.2의 Cypher 쿼리 빌더를 위한 Intent 제공

### 입력 데이터
- **사용자 질의** (str): 자연어 질의 텍스트

### 출력 데이터
- **Intent 딕셔너리** (Dict):
  ```python
  {
    "target_entity_type": str,  # Risk, Opportunity, Event, Technology, Product, Person, general
    "filters": {
      "ticker": str,  # 선택적
      "time_range": str,  # 선택적
      ...
    },
    "query_type": str,  # explain, list, compare, analyze
    "expansion": {
      "include_related_companies": bool
    }
  }
  ```

### Class 구조

#### Class: `IntentExtractor`
Gemini를 활용한 Intent 추출 클래스 (Structured Output 사용)

##### 속성 (Attributes)
- `model` (str): Gemini 모델명 (기본값: "gemini-2.5-flash-lite")
- `client`: Gemini 클라이언트 인스턴스
- `_original_query` (str): 원본 질의 저장

##### 함수 (Methods)

###### `__init__(self, model: str = "gemini-2.5-flash-lite", api_key: Optional[str] = None)`
- **목적**: IntentExtractor 인스턴스 초기화
- **Input 구조 및 내용**:
  - `model` (str, optional): Gemini 모델명
  - `api_key` (str, optional): Gemini API 키 (없으면 환경변수에서 로드)
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. Gemini 클라이언트 초기화
  2. 모델명 설정

###### `extract_intent(self, query: str) -> Dict`
- **목적**: 질의에서 Intent 추출 (비동기, Structured Output 사용)
- **Input 구조 및 내용**:
  - `query` (str): 사용자 질의
- **Output 형식 및 내용**:
  - `Dict`: Intent 딕셔너리
- **함수 내부 동작 방식**:
  1. 프롬프트 생성
  2. Gemini Structured Output API 호출
  3. JSON 파싱 및 Pydantic 모델 검증
  4. 검증 및 정규화
  5. Intent 딕셔너리 반환

###### `extract_intent_sync(self, query: str) -> Dict`
- **목적**: 질의에서 Intent 추출 (동기 버전)
- **Input 구조 및 내용**:
  - `query` (str): 사용자 질의
- **Output 형식 및 내용**:
  - `Dict`: Intent 딕셔너리
- **함수 내부 동작 방식**:
  - 비동기 메서드를 동기로 래핑

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **Gemini Structured Output 활용**
   - Pydantic 모델 기반 구조화된 출력
   - JSON 스키마 자동 생성

2. **질의 유형 분류**
   - explain: 설명 요청
   - list: 목록 요청
   - compare: 비교 요청
   - analyze: 분석 요청

3. **엔티티 추출**
   - 기업 (ticker)
   - 제품
   - 인물
   - 기술

4. **필터 추출**
   - 시간 범위
   - 티커
   - 기타 필터 조건

## 📊 데이터 구조

### 입력 데이터 구조
- **사용자 질의**: 자연어 텍스트 문자열

### 출력 데이터 구조
- **Intent 딕셔너리**:
  ```python
  {
    "target_entity_type": str,  # Risk, Opportunity, Event, Technology, Product, Person, general
    "filters": {
      "ticker": str,  # 선택적
      "time_range": str,  # 선택적
      ...
    },
    "query_type": str,  # explain, list, compare, analyze
    "expansion": {
      "include_related_companies": bool
    }
  }
  ```

### Intent 구조 (Pydantic 모델)
```python
class Intent(BaseModel):
    target_entity_type: Union[str, List[str]]
    filters: Filters
    query_type: str
    expansion: Expansion
```

### 프롬프트 관리
- YAML 파일: `app/prompts/intent_extractor.yaml`

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/query/intent_extractor.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.query.intent_extractor import IntentExtractor

extractor = IntentExtractor()

# Intent 추출
intent = extractor.extract_intent_sync("애플의 기회 요소를 알려줘")

print(f"Target: {intent['target_entity_type']}")
print(f"Ticker: {intent['filters'].get('ticker')}")
print(f"Query Type: {intent['query_type']}")
```

### 에러 핸들링
- API 호출 실패: 예외 처리 및 로깅
- JSON 파싱 실패: 예외 처리 및 로깅
- Pydantic 검증 실패: 예외 처리 및 로깅

## 🔄 상세 알고리즘/프로세스

### Intent 추출 프로세스
1. **프롬프트 생성**
   - YAML 파일에서 프롬프트 로드
   - 질의 텍스트 삽입

2. **Gemini API 호출**
   - Structured Output 사용
   - JSON 스키마 지정
   - 낮은 temperature (일관성)

3. **JSON 파싱**
   - 마크다운 코드 블록 제거
   - JSON 파싱

4. **Pydantic 검증**
   - Intent 모델로 검증
   - 타입 변환 및 정규화

5. **검증 및 정규화**
   - 추가 검증 로직
   - 정규화 수행

6. **Intent 반환**
   - 검증된 Intent 딕셔너리 반환

### 예외 처리
- API 호출 실패: 예외 처리 및 로깅
- JSON 파싱 실패: 예외 처리 및 로깅
- Pydantic 검증 실패: 예외 처리 및 로깅

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY` 또는 `GEMINI_API_KEY`: Gemini API 키 (필수)

### 외부 라이브러리 의존성
- `google-genai`: Gemini API 클라이언트
- `pydantic`: 데이터 검증

### 설정 파일
- `app/prompts/intent_extractor.yaml`: Intent 추출 프롬프트 템플릿

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_extract_intent():
    extractor = IntentExtractor()
    intent = extractor.extract_intent_sync("애플의 기회 요소를 알려줘")
    
    assert "target_entity_type" in intent
    assert "filters" in intent
    assert "query_type" in intent
```

### 통합 테스트 시나리오
- 다양한 질의로 Intent 추출 테스트
- Intent 구조 검증
- 필터 추출 정확도 확인

### 검증 방법
- Intent 구조 확인
- 필터 추출 정확도 확인
- 질의 유형 분류 정확도 확인

## ⚠️ 주의사항

- LLM API 비용 발생
- Structured Output 사용으로 일관성 향상
- 프롬프트 품질이 추출 정확도에 큰 영향
- 낮은 temperature 사용 (일관성)

## 📝 History
