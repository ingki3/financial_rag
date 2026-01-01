# Phase 8.4: 답변 생성 구현

## 📋 Sub-task 개요

검색 결과를 기반으로 자연어 답변을 생성하는 모듈을 구현합니다. LLM을 통한 답변 생성, 출처 정보 포함, 스트리밍 지원을 제공합니다.

### 파일 경로
**파일**: `app/services/query/answer_generator.py`

### Phase 전체 목표 기여
- 자연어 답변 생성
- 출처 정보 포함
- 스트리밍 응답 지원

### 입력 데이터
- **질의** (str): 사용자 질의
- **검색 결과** (List[Dict]): Graph/Vector 검색 결과
- **Intent** (Dict, optional): Intent 추출 결과

### 출력 데이터
- **답변 텍스트** (str): 생성된 답변
- **스트리밍 생성기** (Generator[str]): 스트리밍 답변 생성기

### Class 구조

#### Class: `AnswerGenerator`
검색 결과를 바탕으로 답변 생성 클래스

##### 속성 (Attributes)
- `model` (str): Gemini 모델명
- `client`: Gemini 클라이언트 인스턴스

##### 함수 (Methods)

###### `generate_answer(self, query: str, results: List[Dict], intent: Optional[Dict] = None, max_results: int = 5) -> str`
- **목적**: 답변 생성 (동기)
- **Input 구조 및 내용**:
  - `query` (str): 사용자 질의
  - `results` (List[Dict]): 검색 결과 리스트
  - `intent` (Dict, optional): Intent 추출 결과
  - `max_results` (int): 사용할 최대 결과 수
- **Output 형식 및 내용**:
  - `str`: 생성된 답변 텍스트
- **함수 내부 동작 방식**:
  1. 검색 결과에서 컨텍스트 구성
  2. 프롬프트 생성
  3. LLM 호출
  4. 답변 텍스트 반환

###### `generate_answer_stream(self, query: str, results: List[Dict], intent: Optional[Dict] = None, max_results: int = 5) -> Generator[str, None, None]`
- **목적**: 답변 생성 (스트리밍)
- **Input 구조 및 내용**:
  - `query` (str): 사용자 질의
  - `results` (List[Dict]): 검색 결과 리스트
  - `intent` (Dict, optional): Intent 추출 결과
  - `max_results` (int): 사용할 최대 결과 수
- **Output 형식 및 내용**:
  - `Generator[str, None, None]`: 스트리밍 답변 생성기
- **함수 내부 동작 방식**:
  1. 검색 결과에서 컨텍스트 구성
  2. 프롬프트 생성
  3. LLM 스트리밍 호출
  4. 각 chunk를 yield

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **LLM을 통한 답변 생성**
   - Gemini 모델 사용
   - 검색 결과를 컨텍스트로 활용

2. **출처 정보 포함**
   - 검색 결과의 출처 정보 포함
   - 노드 ID, 타입, 티커 정보 포함

3. **스트리밍 지원**
   - Server-Sent Events (SSE) 지원
   - 실시간 답변 생성

## 📊 데이터 구조

### 입력 데이터 구조
- **검색 결과**:
  ```python
  [
    {
      "node_id": str,
      "node_type": str,
      "entity": str,
      "description": str,
      "ticker": str
    }
  ]
  ```

### 출력 데이터 구조
- **답변 텍스트**: 자연어 답변 문자열

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/query/answer_generator.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.query.answer_generator import AnswerGenerator

generator = AnswerGenerator()

# 동기 답변 생성
answer = generator.generate_answer(
    query="애플의 기회 요소를 알려줘",
    results=search_results,
    intent=intent
)

# 스트리밍 답변 생성
for chunk in generator.generate_answer_stream(
    query="애플의 기회 요소를 알려줘",
    results=search_results
):
    print(chunk, end="", flush=True)
```

### 에러 핸들링
- LLM API 호출 실패: 폴백 답변 반환
- 검색 결과 없음: 안내 메시지 반환

## 🔄 상세 알고리즘/프로세스

### 답변 생성 프로세스
1. **검색 결과 수집**
   - 최대 max_results 개수만큼 사용

2. **컨텍스트 구성**
   - 검색 결과를 텍스트로 변환
   - 출처 정보 포함

3. **프롬프트 생성**
   - YAML 파일에서 프롬프트 로드
   - 질의, 컨텍스트, Intent 정보 포함

4. **LLM 호출**
   - 동기: `generate_content`
   - 스트리밍: `generate_content_stream`

5. **답변 반환**
   - 동기: 답변 텍스트 반환
   - 스트리밍: 각 chunk를 yield

### 예외 처리
- LLM API 호출 실패: 폴백 답변 반환
- 검색 결과 없음: 안내 메시지 반환

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (필수)

### 외부 라이브러리 의존성
- `google-genai`: Gemini API 클라이언트

### 설정 파일
- `app/prompts/answer_generator.yaml`: 답변 생성 프롬프트 템플릿

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_generate_answer():
    generator = AnswerGenerator()
    answer = generator.generate_answer(
        query="테스트 질의",
        results=[{"entity": "Test", "description": "Test description"}]
    )
    assert len(answer) > 0
```

### 통합 테스트 시나리오
- 실제 검색 결과로 답변 생성 테스트
- 스트리밍 동작 확인
- 출처 정보 포함 확인

### 검증 방법
- 답변 텍스트 길이 확인
- 출처 정보 포함 확인
- 스트리밍 동작 확인

## ⚠️ 주의사항

- LLM API 비용 발생
- 프롬프트 품질이 답변 품질에 큰 영향
- 스트리밍 시 에러 처리 중요

## 📝 History
