# 규칙 파일 최종 검토 결과

## 📋 개요

모든 규칙 파일(`agent.mdc`, `docs.mdc`, `plan.mdc`, `prd.mdc`, `tasks.mdc`)을 검토하여 프로젝트 진행 시 발생할 수 있는 문제점을 확인했습니다.

---

## ✅ 정상 작동하는 부분

### 1. Planning Mode 케이스 구분
- ✅ 케이스 1 (Phase/Sub-task 계획): `plan/tasks/`, `plan/plan.md`, `plan/prd.md`에 기록
- ✅ 케이스 2 (중간 점검/대안 탐색): `docs/`에 기록
- ✅ 각 케이스별 저장 위치와 승인 규칙이 명확히 구분됨

### 2. 공통 규칙 통합
- ✅ Phase 번호 체계, Phase 번호 결정 기준, Docs 역할, 일관성 유지 규칙이 `plan.mdc`에 통합됨
- ✅ 다른 파일들은 참조만 하도록 정리됨

### 3. 승인 프로세스
- ✅ `plan/plan.md`, `plan/prd.md` 수정 시 승인 필요 (일관성 있음)
- ✅ `docs/` 하위 파일은 승인 불필요 (명확함)
- ✅ `plan/tasks/` 하위 파일 수정 시 승인 필요

---

## 🔴 발견된 문제점

### 1. Implementation Mode의 "If no plan exists" 규칙 불일치 ✅ 해결됨

**문제점**:
- `agent.mdc` (line 79-81): "If no plan exists: First create a planning document in `docs/`"
- 하지만 이제 Planning Mode에 케이스 1이 추가되어 Phase/Sub-task 계획은 `plan/tasks/`에 기록해야 함

**충돌 상황**:
- Implementation Mode에서 계획이 없을 때 `docs/`에만 생성하도록 되어 있음
- Phase/Sub-task 계획인 경우 `plan/tasks/`에 생성해야 하는데 규칙이 없음

**영향**:
- Phase/Sub-task 계획이 `docs/`에 잘못 생성될 수 있음
- `plan/plan.md`와 `plan/prd.md` 업데이트가 누락될 수 있음

**해결 방안**:
- ✅ Implementation Mode 수정 완료:
  1. 구현 전에 반드시 Phase/Sub-task 확인 및 내용 파악 과정 추가
  2. 계획 파일 존재 여부 확인 프로세스 추가
  3. 계획 파일이 없는 경우 Planning Mode로 전환하여 계획 먼저 수립
  4. 계획 수립 시 `plan/tasks/phase-{N}/phase-{N}-{M}.md`, `plan/plan.md`, `plan/prd.md`에 기록하도록 명시

---

### 2. History 기록 형식 불일치 ✅ 해결됨

**문제점**:
각 모드/케이스별로 History 형식이 다름:

- **agent.mdc 케이스 1** (line 37-49):
  - `Created/Modified Files` (리스트 형식)
  - `Purpose`, `Status`

- **agent.mdc 케이스 2** (line 62-71):
  - `Generated Document` (단일 파일)
  - `Purpose`, `Status`

- **agent.mdc Implementation Mode** (line 87-99):
  - `Modified/Created Files` (리스트 형식)
  - `Purpose`, `Status`
  - `Related Plan Document` (추가 필드)

- **tasks.mdc** (line 91-103):
  - `Modified Files` (리스트 형식)
  - `Synchronized Files` (추가 필드)
  - `Purpose`, `Status`

- **docs.mdc** (line 107-115):
  - `Generated Document` (단일 파일)
  - `Purpose`, `Status`

**충돌 상황**:
- 같은 `plan/tasks/phase-{N}/phase-{N}.md`에 기록되는데 형식이 다름
- AI가 어떤 형식을 사용해야 할지 혼란스러울 수 있음

**영향**:
- History 섹션이 일관성 없게 작성될 수 있음
- 검색 및 추적이 어려울 수 있음

**해결 방안**:
- ✅ 통일된 History 기록 형식 정의 및 적용:
  - `plan.mdc`에 통일된 History 형식 정의 추가
  - 공통 필드: `Date`, `User Request`, `Purpose`, `Status`
  - 선택적 필드: `Created/Modified Files`, `Generated Document`, `Synchronized Files`, `Related Plan Document`
  - 각 케이스별 사용 가이드 제공
  - 모든 규칙 파일(`agent.mdc`, `tasks.mdc`, `docs.mdc`)에 통일된 형식 적용

---

### 3. 케이스 1에서 `plan/tasks` 파일 생성 규칙 누락 ✅ 해결됨

**문제점**:
- `agent.mdc` 케이스 1 (line 30-32): `plan/tasks/phase-{N}/phase-{N}-{M}.md` 작성 명시
- 하지만 파일이 존재하지 않을 때의 처리 방법이 명시되지 않음
- 케이스 2에는 "If the plan/tasks file doesn't exist: Create it first" 규칙이 있음 (line 72)

**충돌 상황**:
- 케이스 1에서 `plan/tasks/phase-{N}/` 폴더나 파일이 없을 때 어떻게 할지 불명확

**영향**:
- 파일 생성 누락 가능성
- 오류 발생 가능성

**해결 방안**:
- ✅ 케이스 1에 파일 존재 여부 확인 및 생성 규칙 추가 완료:
  - `plan/tasks/phase-{N}/` 폴더 존재 여부 확인
  - `plan/tasks/phase-{N}/phase-{N}.md` 파일 존재 여부 확인
  - 파일/폴더가 없는 경우 먼저 생성하도록 명시

---

### 4. `plan/tasks` 수정 시 승인 규칙과 동기화 규칙 충돌 ✅ 해결됨

**문제점**:
- `tasks.mdc` (line 15): `plan/tasks/` 수정 전 승인 필요
- `tasks.mdc` (line 46-56): Tasks 문서 수정 시 `plan/plan.md`와 `plan/prd.md` 동기화 필요
- 하지만 `plan/plan.md`와 `plan/prd.md` 수정 시에도 승인 필요 (`agent.mdc` line 14)

**충돌 상황**:
- Tasks 문서를 수정하면 자동으로 `plan/plan.md`와 `plan/prd.md`를 동기화해야 하는데, 이때도 승인이 필요한지 불명확
- 승인을 받아야 하는지, 자동으로 동기화해도 되는지 모호

**영향**:
- 동기화가 지연되거나 누락될 수 있음
- 승인 프로세스가 복잡해질 수 있음

**해결 방안**:
- ✅ 동기화를 위한 변경 시에도 승인 필요하도록 명시:
  - `tasks.mdc`의 동기화 프로세스에 "동기화 승인 요청" 단계 추가
  - 동기화 전 사용자 승인을 받은 후 동기화 수행하도록 명시
  - 동기화 체크리스트에 승인 확인 항목 추가

---

### 5. `docs.mdc`의 History 기록 규칙과 `agent.mdc` 케이스 2 중복 ✅ 해결됨

**문제점**:
- `docs.mdc` (line 97-115): `docs/` 문서 생성 시 History 기록 규칙
- `agent.mdc` 케이스 2 (line 60-73): 동일한 History 기록 규칙

**충돌 상황**:
- 동일한 내용이 두 파일에 중복
- `docs.mdc`는 `docs/` 파일 편집 시 적용되는 규칙인데, History 기록은 `plan/tasks/`에 기록

**영향**:
- 규칙 변경 시 두 파일을 모두 수정해야 함
- 불일치 가능성

**해결 방안**:
- ✅ `docs.mdc`에서 History 기록 규칙 간소화:
  - 중복된 사용 예시 제거
  - `agent.mdc` 케이스 2의 "Record in plan/tasks" 부분 참조하도록 변경
  - `plan.mdc`의 "History 기록 형식" 섹션 참조 유지
  - History 기록 위치와 형식만 간단히 명시

---

### 6. Phase 번호 결정 기준 참조 불일치 ✅ 해결됨

**문제점**:
- `agent.mdc` 케이스 1 (line 39): "Phase numbering 결정 기준: `plan.mdc`의 'Phase 번호 결정 기준' 섹션을 참조하세요."
- `agent.mdc` 케이스 2 (line 62): 동일한 참조
- `docs.mdc` (line 31): 동일한 참조
- 하지만 `plan.mdc`의 "Phase 번호 결정 기준" (line 30)은 "Planning Mode에서 문서를 생성할 때"라고 명시되어 있음
- Implementation Mode에서도 Phase 번호를 결정해야 할 수 있지만 명시적인 참조가 없음

**충돌 상황**:
- 케이스 1은 Planning Mode이지만, `plan/tasks/`에 기록하는 경우도 Planning Mode인지 불명확
- Implementation Mode에서도 Phase 번호를 결정해야 할 수 있음
- Phase 번호 결정 기준이 Planning Mode에만 국한되어 보임

**영향**:
- Phase 번호 결정 기준이 Planning Mode에만 국한되어 보일 수 있음
- Implementation Mode에서 계획 파일이 없을 때 Phase 번호 결정 기준이 불명확

**해결 방안**:
- ✅ `plan.mdc`의 "Phase 번호 결정 기준" 설명을 더 일반적으로 수정:
  - "Planning Mode에서 문서를 생성할 때" → "문서를 생성하거나 Phase 번호를 결정할 때"로 변경
  - 적용 범위 명시: Planning Mode, Implementation Mode, 기타 모든 상황
- ✅ Implementation Mode에 Phase 번호 결정 기준 참조 추가:
  - 계획 파일이 없는 경우 Planning Mode로 전환할 때 Phase 번호 결정 기준 참조 추가

---

## 🟡 개선 권장 사항

### 1. History 기록 형식 통일

**제안**:
- 공통 필드: `Date`, `User Request`, `Purpose`, `Status`
- 선택적 필드: `Created/Modified Files`, `Generated Document`, `Synchronized Files`, `Related Plan Document`
- 각 케이스별로 필요한 필드만 사용하도록 명시

### 2. 파일 존재 여부 확인 프로세스 명시

**제안**:
- 모든 케이스에서 파일/폴더 존재 여부 확인 프로세스 추가
- 존재하지 않을 때의 처리 방법 명시

### 3. 동기화 승인 규칙 명확화

**제안**:
- Tasks 문서 수정으로 인한 자동 동기화는 승인 불필요로 명시
- 또는 모든 동기화도 승인 필요로 명시
- 일관성 있게 규칙 정의

---

## 📋 수정 우선순위

### 즉시 수정 필요 (Critical)

1. **Implementation Mode의 "If no plan exists" 규칙 수정** ✅ 완료
   - ✅ 구현 전 Phase/Sub-task 확인 및 내용 파악 프로세스 추가
   - ✅ 계획 파일 존재 여부 확인 프로세스 추가
   - ✅ 계획 파일이 없는 경우 Planning Mode로 전환하여 계획 먼저 수립하도록 수정

2. **케이스 1에서 파일 생성 규칙 추가** ✅ 완료
   - ✅ `plan/tasks/phase-{N}/` 폴더나 파일이 없을 때 생성 규칙 추가

3. **동기화 승인 규칙 명확화** ✅ 완료
   - ✅ 동기화를 위한 변경 시에도 승인 필요하도록 명시
   - ✅ `tasks.mdc`의 동기화 프로세스에 "동기화 승인 요청" 단계 추가
   - ✅ 동기화 체크리스트에 승인 확인 항목 추가

### 개선 권장 (Medium)

4. **History 기록 형식 통일** ✅ 완료
   - ✅ `plan.mdc`에 통일된 History 형식 정의 추가
   - ✅ 공통 필드와 선택적 필드 명확히 정의
   - ✅ 각 케이스별 사용 가이드 제공
   - ✅ 모든 규칙 파일에 통일된 형식 적용

5. **docs.mdc의 History 기록 규칙 정리** ✅ 완료
   - ✅ `docs.mdc`에서 History 기록 규칙 간소화
   - ✅ 중복된 사용 예시 제거
   - ✅ `agent.mdc` 케이스 2 참조로 변경
   - ✅ `plan.mdc` 참조 유지

6. **Phase 번호 결정 기준 설명 개선** ✅ 완료
   - ✅ `plan.mdc`의 "Phase 번호 결정 기준" 설명을 더 일반적으로 수정
   - ✅ 적용 범위 명시 (Planning Mode, Implementation Mode, 기타 모든 상황)
   - ✅ Implementation Mode에 Phase 번호 결정 기준 참조 추가

---

## ✅ 검토 완료 항목

- ✅ Planning Mode 케이스 구분이 명확함
- ✅ 공통 규칙이 `plan.mdc`에 통합됨
- ✅ 승인 프로세스가 일관성 있게 정의됨
- ✅ Phase/Sub-task 변경 프로세스가 상세히 정의됨
- ✅ 각 파일의 역할이 명확히 구분됨

---

## 📅 작성일

2025-01-27

