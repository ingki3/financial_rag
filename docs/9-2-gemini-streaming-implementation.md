# Gemini 스트리밍 구현 가이드

## 📋 확인된 사항

### 1. `google.genai` 패키지의 스트리밍 메서드

`google.genai` 패키지 (버전 1.56.0)에서는 **`generate_content_stream`** 메서드를 제공합니다.

**메서드 시그니처:**
```python
client.models.generate_content_stream(
    model: str,
    contents: Union[Content, ContentDict, str, File, ...],
    config: Optional[GenerateContentConfig] = None
) -> Iterator[GenerateContentResponse]
```

### 2. 반환 타입

- 반환값: `Iterator[GenerateContentResponse]` (Generator)
- 각 chunk는 `GenerateContentResponse` 객체
- 텍스트는 `chunk.text` 속성 또는 `chunk.candidates[0].content.parts[0].text`에서 추출 가능

### 3. 테스트 결과

✅ 스트리밍이 정상적으로 작동함
- 각 chunk에서 텍스트를 실시간으로 받을 수 있음
- 마지막 chunk는 `finish_reason=STOP`으로 종료 신호를 보냄

---

## 🔧 구현 방법

### `AnswerGenerator.generate_answer_stream()` 메서드 추가

```python
from typing import Generator, Dict, List, Optional

def generate_answer_stream(
    self,
    query: str,
    results: List[Dict],
    intent: Optional[Dict] = None,
    max_results: int = 5
) -> Generator[str, None, None]:
    """
    검색 결과를 바탕으로 스트리밍 답변 생성
    
    Args:
        query: 사용자 질의
        results: 검색 결과 리스트
        intent: Intent 객체 (선택적)
        max_results: 답변 생성에 사용할 최대 결과 수
        
    Yields:
        답변 텍스트 청크 (str)
    """
    if not results:
        yield "죄송합니다. 검색 결과를 찾을 수 없습니다."
        return
    
    # 상위 N개 결과만 사용
    top_results = results[:max_results]
    
    # 컨텍스트 구성
    context = self._build_context(top_results, intent)
    
    # Prompt 생성
    prompt = self._build_prompt(query, context, intent)
    
    try:
        # generate_content_stream 사용
        response_stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config={
                "temperature": 0.7,
            }
        )
        
        # 각 chunk에서 텍스트 추출하여 yield
        for chunk in response_stream:
            text = None
            
            # 방법 1: chunk.text 속성 확인
            if hasattr(chunk, 'text') and chunk.text:
                text = chunk.text
            # 방법 2: candidates 구조에서 추출
            elif hasattr(chunk, 'candidates') and chunk.candidates:
                for candidate in chunk.candidates:
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text = part.text
                                    break
                        elif hasattr(candidate.content, 'text') and candidate.content.text:
                            text = candidate.content.text
                            break
                    if text:
                        break
            
            if text:
                yield text
                
    except Exception as e:
        logger.error(f"Failed to generate streaming answer: {e}")
        # 폴백: 간단한 요약 반환
        fallback = self._generate_fallback_answer(query, top_results)
        yield fallback
```

---

## 🚀 FastAPI에서 사용하기

### Server-Sent Events (SSE) 스트리밍 응답

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.services.query.answer_generator import AnswerGenerator
from app.services.query.query_engine import QueryEngine

app = FastAPI()

@app.post("/answer")
async def answer_stream(request: AnswerRequest):
    """
    질의에 대한 답변을 스트리밍으로 반환
    """
    query_engine = get_query_engine()  # 의존성 주입
    
    # 질의 처리
    result = query_engine.query(
        user_query=request.query,
        use_vector_search=request.use_vector_search,
        top_k=request.top_k,
        generate_answer=False  # 답변은 스트리밍으로 생성
    )
    
    # AnswerGenerator 인스턴스
    answer_generator = query_engine.answer_generator
    
    # 스트리밍 생성기
    def generate():
        for chunk in answer_generator.generate_answer_stream(
            query=request.query,
            results=result["merged_results"],
            intent=result["intent"]
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

## 📝 참고사항

### 1. Vertex AI vs Gemini API

현재 프로젝트는 **Gemini API** (`google.genai` 패키지)를 사용하고 있습니다.
- Vertex AI의 경우 OpenAI 호환 API를 사용할 수 있지만, 현재는 Gemini API를 직접 사용

### 2. 스트리밍 vs 일반 생성

- **일반 생성**: `generate_content()` - 전체 응답을 한 번에 반환
- **스트리밍**: `generate_content_stream()` - 청크 단위로 실시간 반환

### 3. 에러 처리

- 스트리밍 중 에러 발생 시 폴백 답변을 yield
- 네트워크 오류 등에 대한 적절한 에러 핸들링 필요

---

## ✅ 테스트 결과

```
✅ 스트리밍 테스트 성공!
- 총 청크 수: 24
- 전체 응답 길이: 1017 문자
- 각 chunk에서 텍스트 추출 성공
```

---

## 🔗 참고 문서

- [Google Cloud Vertex AI - Gemini 스트리밍 샘플](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-chat-completions-streaming?hl=ko)
- `google-genai` 패키지 버전: 1.56.0

