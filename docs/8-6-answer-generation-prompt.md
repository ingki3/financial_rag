# 답변 생성 프롬프트

답변 생성에 사용되는 프롬프트 템플릿입니다.

**파일**: `app/services/answer_generator.py`  
**메서드**: `_build_prompt()`

---

## 프롬프트 템플릿

```python
prompt = f"""당신은 금융 공시 문서 기반 Knowledge Graph 질의 응답 시스템입니다.

사용자 질의: {query}

검색 결과:
{context}

위 검색 결과를 바탕으로 사용자 질의에 대한 명확하고 구조화된 답변을 생성하세요.

답변 작성 가이드:
1. 검색 결과의 핵심 내용을 요약하여 설명하세요.
2. 구체적인 데이터나 숫자가 있다면 포함하세요.
3. 여러 결과가 있는 경우, 중요도 순으로 정리하세요.
4. 한국어로 자연스럽게 작성하세요.
5. 질의 유형이 "{query_type}"이므로 이에 맞는 형식으로 답변하세요.
   - "explain": 상세한 설명
   - "list": 목록 형식
   - "compare": 비교 형식
   - "analyze": 분석 형식
6. 검색 결과가 내용이 없을 경우에는 "참고할 수 있는 정보가 없어, 답변 할 수 없다"고 대답하시오.

답변:"""
```

---

## 컨텍스트 구성

검색 결과는 다음과 같은 형식으로 컨텍스트에 포함됩니다:

```
[결과 1]
타입: Opportunity
제목: Americas Market Expansion
설명: The Americas segment saw a significant increase in net sales, rising from $116.5 billion to $129.9 billion for the nine-month period. Operating income for this region also grew, reaching $48.8 billion as of June 25, 2022.
기업: AAPL

[결과 2]
타입: Risk
제목: Intense Global Competition
설명: The Company faces aggressive price competition and rapid technological change from competitors with substantial resources...
기업: TSLA

...
```

**구성 방법** (`_build_context` 메서드):
- 각 검색 결과에 대해:
  - `[결과 N]` 형식으로 번호 부여
  - 노드 타입 (node_type)
  - 제목 (entity 또는 name)
  - 설명 (description)
  - 기업 티커 (ticker, 있는 경우)

---

## 사용 모델

- **모델**: `gemini-2.5-flash-lite` (기본값)
- **Temperature**: 0.7
- **최대 결과 수**: 5개 (기본값, `max_results` 파라미터로 조정 가능)

---

## 질의 유형별 답변 형식

### 1. "explain" (설명)
- 상세한 설명 형식
- 배경 정보와 맥락 포함
- 예: "구글의 AI 기술에 대해 알려줘"

### 2. "list" (목록)
- 목록 형식으로 정리
- 각 항목을 명확하게 구분
- 예: "애플의 기회 요소는?"

### 3. "compare" (비교)
- 비교 형식으로 정리
- 유사점과 차이점 명시
- 예: "애플과 테슬라의 리스크를 비교해줘"

### 4. "analyze" (분석)
- 분석 형식으로 정리
- 인사이트와 결론 포함
- 예: "테슬라의 재무적 기회 요소를 분석해줘"

---

## 실제 사용 예시

### 입력
- **질의**: "애플의 기회 요소는?"
- **검색 결과**: 5개의 Opportunity 노드
- **Intent**: `{"query_type": "list", ...}`

### 프롬프트 (실제 생성되는 형태)

```
당신은 금융 공시 문서 기반 Knowledge Graph 질의 응답 시스템입니다.

사용자 질의: 애플의 기회 요소는?

검색 결과:
[결과 1]
타입: Opportunity
제목: Americas Market Expansion
설명: The Americas segment saw a significant increase in net sales, rising from $116.5 billion to $129.9 billion for the nine-month period. Operating income for this region also grew, reaching $48.8 billion as of June 25, 2022.
기업: AAPL

[결과 2]
타입: Opportunity
제목: Ecosystem Integration and Brand Loyalty
설명: The Company designs and develops nearly the entire solution for its products, including hardware, operating systems, and services. This integrated approach allows for a unique customer experience and strengthens brand loyalty.
기업: AAPL

...

위 검색 결과를 바탕으로 사용자 질의에 대한 명확하고 구조화된 답변을 생성하세요.

답변 작성 가이드:
1. 검색 결과의 핵심 내용을 요약하여 설명하세요.
2. 구체적인 데이터나 숫자가 있다면 포함하세요.
3. 여러 결과가 있는 경우, 중요도 순으로 정리하세요.
4. 한국어로 자연스럽게 작성하세요.
5. 질의 유형이 "list"이므로 이에 맞는 형식으로 답변하세요.
   - "explain": 상세한 설명
   - "list": 목록 형식
   - "compare": 비교 형식
   - "analyze": 분석 형식

답변:
```

---

## 폴백 답변

LLM 호출이 실패할 경우, 간단한 요약 형식의 폴백 답변을 생성합니다:

```
'{query}'에 대한 검색 결과를 찾았습니다:

1. {entity}: {description_preview}
2. {entity}: {description_preview}
...
```

---

## 코드 위치

- **파일**: `app/services/answer_generator.py`
- **주요 메서드**:
  - `generate_answer()`: 답변 생성 메인 메서드
  - `_build_prompt()`: 프롬프트 생성
  - `_build_context()`: 컨텍스트 구성
  - `_generate_fallback_answer()`: 폴백 답변 생성

