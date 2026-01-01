# Phase 8.5: API 엔드포인트 구현

## 📋 Sub-task 개요

FastAPI를 사용하여 REST API 엔드포인트를 구현합니다. `/answer` 엔드포인트를 통해 질의 응답을 제공하고, Server-Sent Events (SSE)를 지원합니다.

### 파일 경로
**파일**: `app/api/routes/answer.py`

### Phase 전체 목표 기여
- REST API 엔드포인트 제공
- 스트리밍 응답 지원
- 에러 처리

### 입력 데이터
- **AnswerRequest** (Pydantic 모델):
  ```python
  {
    "query": str,  # 사용자 질의
    "use_vector_search": bool,  # Vector 검색 사용 여부
    "top_k": int  # 반환할 결과 수
  }
  ```

### 출력 데이터
- **Server-Sent Events (SSE) 스트리밍 응답**: 실시간 답변 텍스트

### Class 구조
**해당 없음** (FastAPI 라우터)

## 🎯 주요 기능

1. **`/answer` 엔드포인트**
   - POST 메서드
   - 질의 응답 (스트리밍)
   - QueryEngine을 통한 질의 처리

2. **Server-Sent Events (SSE) 지원**
   - 실시간 답변 생성
   - 스트리밍 응답

3. **에러 처리**
   - 예외 처리 및 에러 메시지 반환
   - 로깅

## 📊 데이터 구조

### 입력 데이터 구조
- **AnswerRequest**:
  ```python
  {
    "query": str,
    "use_vector_search": bool,
    "top_k": int
  }
  ```

### 출력 데이터 구조
- **SSE 스트리밍 응답**:
  ```
  data: 답변 텍스트 chunk 1\n\n
  data: 답변 텍스트 chunk 2\n\n
  ...
  data: [DONE]\n\n
  ```

## 💻 코드 예시 및 전체 코드 구현

### API 엔드포인트 구현
전체 코드는 `app/api/routes/answer.py` 파일을 참조하세요.

### 엔드포인트 구조
```python
@router.post("")
async def answer_stream(
    request: AnswerRequest,
    query_engine: QueryEngine = Depends(get_query_engine)
):
    """질의에 대한 답변을 스트리밍으로 반환"""
    # 질의 처리
    result = query_engine.query(
        user_query=request.query,
        use_vector_search=request.use_vector_search,
        top_k=request.top_k,
        generate_answer=False
    )
    
    # 스트리밍 생성기
    def generate():
        for chunk in answer_generator.generate_answer_stream(...):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### 사용 예시
```bash
# API 호출
curl -X POST "http://localhost:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "애플의 기회 요소를 알려줘",
    "use_vector_search": true,
    "top_k": 10
  }'
```

### 에러 핸들링
- QueryEngine 초기화 실패: 에러 메시지 반환
- 답변 생성 실패: 에러 메시지 반환
- 스트리밍 실패: 에러 메시지 반환

## 🔄 상세 알고리즘/프로세스

### API 요청 처리 프로세스
1. **요청 수신**
   - AnswerRequest 파싱
   - QueryEngine 의존성 주입

2. **질의 처리**
   - QueryEngine.query() 호출
   - Intent 추출, Graph/Vector 검색, 결과 통합

3. **스트리밍 답변 생성**
   - AnswerGenerator.generate_answer_stream() 호출
   - 각 chunk를 SSE 형식으로 전송

4. **완료 신호 전송**
   - `[DONE]` 메시지 전송

### 예외 처리
- QueryEngine 초기화 실패: 에러 메시지 반환
- 답변 생성 실패: 에러 메시지 반환
- 스트리밍 실패: 에러 메시지 반환

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키
- `FALKORDB_HOST`: FalkorDB 호스트
- `FALKORDB_PORT`: FalkorDB 포트

### 외부 라이브러리 의존성
- `fastapi`: FastAPI 프레임워크
- `pydantic`: 데이터 검증

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_answer_endpoint():
    # API 엔드포인트 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 API 호출 테스트
- 스트리밍 응답 확인
- 에러 처리 확인

### 검증 방법
- API 응답 상태 코드 확인
- 스트리밍 응답 형식 확인
- 답변 내용 확인

## ⚠️ 주의사항

- CORS 설정 필요 (프로덕션에서는 특정 도메인으로 제한)
- 스트리밍 응답 시 타임아웃 설정 고려
- 에러 처리 중요

## 📝 History
