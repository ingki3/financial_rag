# Risk Factors 섹션에서 Opportunities 추출 이유 분석

## 문제 상황

`data/extracted/AAPL/10-K/0000320193-23-000106.json` 파일을 보면, `risk_factors` 섹션에서 다음과 같은 `opportunities`가 추출되었습니다:

1. **Integrated Ecosystem Strategy** - 하드웨어, 소프트웨어, 서비스 통합
2. **Service Segment Expansion** - 서비스 세그먼트 확장
3. **Global Distribution Network** - 글로벌 유통 네트워크
4. **Payments and Financial Services** - Apple Pay, Apple Card 등
5. **Intellectual Property Differentiation** - 지적재산권 차별화

## 왜 이런 결과가 나왔는가?

### 1. 프롬프트 설계의 특성

현재 `triplet_extractor.yaml` 프롬프트는 **섹션과 무관하게** 모든 카테고리를 추출하도록 설계되어 있습니다:

```yaml
Task:
  Extract up to 10 items for each of the following categories:
  1) Opportunities: growth drivers, market opportunities, competitive advantages
  2) Risks: risk factors, regulatory risks, competitive threats, operational risks
  ...
```

프롬프트는 섹션 이름(`risk_factors`)을 컨텍스트로 제공하지만, **"해당 섹션에 없는 카테고리는 빈 배열을 반환하라"**는 명시적 지시가 없습니다. 대신:

> "If a category has no extractable items, return an empty array [] for it."

이 지시는 "추출할 수 있는 항목이 없으면" 빈 배열을 반환하라는 의미이지, "이 섹션에서는 이 카테고리를 찾지 말라"는 의미가 아닙니다.

### 2. Risk Factors 섹션의 실제 내용 구조

SEC 공시의 Risk Factors 섹션은 단순히 위험만 나열하지 않습니다. 실제로는 다음과 같은 구조로 작성됩니다:

#### A. 위험 설명 + 완화 요소

**원문 예시:**
> "The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include... a strong third-party software and accessories ecosystem..."

**맥락:**
- 위험: "경쟁이 치열하고 기술 변화가 빠르다"
- 완화 요소: "하지만 우리는 통합 생태계를 가지고 있어 경쟁 우위가 있다"

LLM은 이 "완화 요소"를 **opportunity**로 해석했습니다.

#### B. 위험 논의 중 기회 언급

**원문 예시:**
> "The Company is focused on expanding its market opportunities within its services segment, including advertising, cloud services, and digital content platforms."

**맥락:**
- Risk Factors 섹션에서도 회사가 위험을 완화하기 위한 전략이나 기회를 언급합니다
- "이 위험에 직면하지만, 우리는 서비스 세그먼트 확장이라는 기회를 추구하고 있다"

#### C. 경쟁 우위 설명

**원문 예시:**
> "The Company utilizes a robust multi-channel distribution strategy involving both direct retail and online stores as well as indirect channels..."

**맥락:**
- 위험: "유통 채널 의존성"
- 완화 요소: "하지만 우리는 강력한 다채널 유통 네트워크를 보유하고 있다"

이런 "완화 요소"들이 LLM에 의해 **competitive advantage** 또는 **opportunity**로 해석되었습니다.

### 3. LLM의 해석 방식

LLM(Gemini)은 다음과 같이 추론했습니다:

1. **문맥 분석**: Risk Factors 섹션이지만, 긍정적인 요소들이 언급됨
2. **의미 추출**: "통합 생태계", "서비스 확장", "유통 네트워크" 등은 경쟁 우위나 성장 동력으로 해석 가능
3. **카테고리 분류**: 프롬프트의 "Opportunities: growth drivers, market opportunities, competitive advantages" 정의에 부합
4. **결과 생성**: 해당 항목들을 opportunities로 분류

### 4. 실제 원문에서의 맥락

파싱된 `risk_factors` 섹션을 보면:

```
The Company designs and develops nearly the entire solution for its products, 
including the hardware, operating system, numerous software applications and 
related services. Principal competitive factors important to the Company include 
price, product and service features (including security features), relative price 
and performance, product and service quality and reliability, design innovation, 
a strong third-party software and accessories ecosystem...
```

이 문장은:
- **위험 맥락**: "경쟁이 치열하다"는 위험을 설명하는 중
- **완화 요소**: "하지만 우리는 통합 솔루션과 생태계를 가지고 있다"
- **LLM 해석**: "통합 생태계 = competitive advantage = opportunity"

## 결론

### 이것이 문제인가?

**아니요, 이것은 실제로 유용한 정보입니다:**

1. **위험 완화 전략 파악**: Risk Factors에서 추출된 opportunities는 회사가 위험을 어떻게 완화하려는지 보여줍니다
2. **경쟁 우위 식별**: 위험 논의 중 언급된 강점들은 실제 경쟁 우위일 수 있습니다
3. **전략적 인사이트**: 위험과 기회의 상관관계를 이해할 수 있습니다

### 개선 방안 (선택사항)

만약 섹션별로 엄격하게 분리하고 싶다면:

1. **프롬프트 수정**: 섹션별로 추출 가능한 카테고리를 명시
   ```yaml
   - Section: risk_factors
     Extract only: risks, strategies (risk mitigation strategies)
   ```

2. **후처리 필터링**: 섹션별로 허용된 카테고리만 유지

3. **현재 방식 유지**: 섹션 정보(`source_section`)를 유지하여 사용자가 필터링 가능

현재 방식은 `source_section` 필드를 통해 출처를 추적할 수 있으므로, 사용자가 필요에 따라 필터링하거나 모두 활용할 수 있습니다.














