# 규칙 파일 충돌 및 중복 분석

## 📋 개요

모든 규칙 파일(`agent.mdc`, `docs.mdc`, `plan.mdc`, `prd.mdc`, `tasks.mdc`)을 검토하여 프로젝트 진행 시 발생할 수 있는 문제점과 중복 내용을 분석했습니다.

---

## 🔴 발생 가능한 문제 및 충돌 상황

### 1. 승인 프로세스 중복 및 불일치

**문제점**:
- `agent.mdc` (line 14): `plan/prd.md` 또는 `plan/plan.md` 수정 전 승인 필요
- `plan.mdc` (line 15): `plan/plan.md` 수정 전 승인 필요
- `prd.mdc` (line 15): `plan/prd.md` 수정 전 승인 필요
- `tasks.mdc` (line 15): `plan/tasks/` 하위 파일 수정 전 승인 필요
- `docs.mdc` (line 25): `docs/` 하위 파일 수정 전 승인 필요 (중요한 변경사항인 경우)

**충돌 상황**:
- `tasks.mdc`에서 `plan/plan.md`와 `plan/prd.md`를 동기화할 때, `agent.mdc`의 승인 규칙과 충돌
- `docs.mdc`는 "중요한 변경사항인 경우"만 승인 필요로 되어 있어 다른 규칙과 불일치

**영향**:
- AI가 승인을 요청해야 할 시점을 판단하기 어려움
- 동기화 과정에서 승인 프로세스가 중복될 수 있음

**해결 방안**:
- 승인 프로세스를 `agent.mdc`에만 명시하고, 다른 파일에서는 참조만 하도록 통일
- `docs.mdc`의 승인 규칙을 다른 파일과 일치시키거나 명확히 구분

---

### 2. History 기록 위치 및 형식 불일치

**문제점**:
- `agent.mdc` (line 44, 69): `plan/tasks/phase-{N}/phase-{N}.md`에 History 기록
- `docs.mdc` (line 115): `plan/tasks/phase-{N}/phase-{N}.md`에 History 기록
- `tasks.mdc` (line 89): `phase-{N}.md` 파일의 History 섹션에 기록

**충돌 상황**:
- History 기록 형식이 다름:
  - `agent.mdc` (Planning Mode): `Generated Document`, `Purpose`, `Status`
  - `agent.mdc` (Implementation Mode): `Modified/Created Files`, `Purpose`, `Status`, `Related Plan Document`
  - `docs.mdc`: `Generated Document`, `Purpose`, `Status`
  - `tasks.mdc`: `Modified Files`, `Synchronized Files`, `Purpose`, `Status`

**영향**:
- History 항목의 형식이 일관되지 않음
- AI가 어떤 형식을 사용해야 할지 혼란스러울 수 있음

**해결 방안**:
- History 기록 형식을 통일하거나, 각 모드별로 명확히 구분
- History 형식 가이드를 별도 섹션으로 분리

---

### 3. Phase 번호 결정 기준 중복

**문제점**:
- `agent.mdc` (line 36-41): Planning Mode에서 Phase 번호 결정 기준
- `docs.mdc` (line 39-47): Phase 번호 결정 기준 (동일한 내용)

**충돌 상황**:
- 동일한 내용이 두 파일에 중복되어 있음
- `docs.mdc`는 `agent.mdc`의 Planning Mode 규칙을 참조해야 함

**영향**:
- 규칙이 변경될 때 두 파일을 모두 수정해야 함
- 불일치 발생 가능성

**해결 방안**:
- `docs.mdc`에서 Phase 번호 결정 기준을 삭제하고 `agent.mdc` 참조로 대체

---

### 4. Phase/Sub-task 변경 프로세스 중복

**문제점**:
- `agent.mdc` (line 15-24): Phase/Sub-task 변경 시 일관성 유지 규칙 (요약)
- `tasks.mdc` (line 105-167): Phase/Sub-task 추가/변경/삭제 프로세스 (상세)
- `plan.mdc` (line 255-268): Phase/Sub-task 추가/변경/삭제 시 (요약, tasks.mdc 참조)

**충돌 상황**:
- `agent.mdc`와 `plan.mdc`에 요약만 있고, `tasks.mdc`에 상세 내용이 있음
- `plan.mdc`는 `tasks.mdc`를 참조하지만, `agent.mdc`는 독립적으로 규칙을 명시

**영향**:
- 규칙이 변경될 때 여러 파일을 수정해야 함
- 일관성 유지가 어려움

**해결 방안**:
- `agent.mdc`와 `plan.mdc`에서 상세 프로세스를 삭제하고 `tasks.mdc` 참조로 통일

---

### 5. 문서 동기화 책임 모호

**문제점**:
- `tasks.mdc` (line 46-56): Tasks 문서 수정 시 `plan/plan.md`와 `plan/prd.md` 동기화
- `plan.mdc` (line 16-18): `plan/plan.md` 수정 시 `plan/prd.md`와 `plan/tasks/` 확인
- `agent.mdc` (line 17-21): Phase/Sub-task 변경 시 전체 문서 동기화

**충돌 상황**:
- 각 문서가 수정될 때 다른 문서를 동기화해야 하는데, 순환 참조 가능성
- 어떤 문서가 주도적으로 동기화를 수행해야 하는지 불명확

**영향**:
- 동기화 누락 가능성
- 중복 동기화 가능성

**해결 방안**:
- 문서 간 동기화 우선순위 명확화
- 단방향 동기화 규칙 정의 (예: `tasks/` → `plan.md` → `prd.md`)

---

### 6. `docs/` 폴더 역할 중복 설명

**문제점**:
- `agent.mdc` (line 33): `docs/` 역할 설명
- `docs.mdc` (line 11-21): `docs/` 역할 설명 (더 상세)
- `plan.mdc` (line 144): `docs/` 역할 설명 (참고)

**충돌 상황**:
- 동일한 내용이 여러 파일에 중복
- `plan.mdc`는 참고로만 언급하지만, `agent.mdc`와 `docs.mdc`는 상세 설명

**영향**:
- 규칙 변경 시 여러 파일 수정 필요
- 불일치 가능성

**해결 방안**:
- `agent.mdc`와 `plan.mdc`에서 `docs/` 역할 설명을 간소화하고 `docs.mdc` 참조로 통일

---

### 7. 파일 명명 규칙 중복

**문제점**:
- `agent.mdc` (line 34): `docs/` 파일 명명 규칙
- `docs.mdc` (line 29-59): 파일 명명 규칙 (더 상세)
- `tasks.mdc` (line 23-28): `plan/tasks/` 파일 명명 규칙
- `plan.mdc` (line 146-151): `plan/tasks/` 파일 명명 규칙

**충돌 상황**:
- `docs/` 파일 명명 규칙이 `agent.mdc`와 `docs.mdc`에 중복
- `plan/tasks/` 파일 명명 규칙이 `tasks.mdc`와 `plan.mdc`에 중복

**영향**:
- 규칙 변경 시 여러 파일 수정 필요

**해결 방안**:
- `agent.mdc`에서 `docs/` 파일 명명 규칙을 간소화하고 `docs.mdc` 참조
- `plan.mdc`에서 `plan/tasks/` 파일 명명 규칙을 간소화하고 `tasks.mdc` 참조

---

### 8. Phase 번호 체계 설명 중복

**문제점**:
- `agent.mdc` (line 13): Phase 번호 체계 설명
- `docs.mdc` (line 30-32): Phase 번호 체계 (파일 명명 규칙 내)
- `tasks.mdc` (line 30-32): Phase 번호 체계
- `plan.mdc` (line 100): Sub-task 번호 체계

**충돌 상황**:
- Phase 번호 체계가 여러 파일에 분산되어 있음

**영향**:
- 규칙 변경 시 여러 파일 수정 필요

**해결 방안**:
- Phase 번호 체계를 `agent.mdc`에만 명시하고, 다른 파일에서는 참조만 하도록 통일

---

## 🟡 중복 내용 (삭제 가능)

### 1. `docs.mdc`에서 삭제 가능한 내용

#### Phase 번호 결정 기준 (line 39-47)
- **이유**: `agent.mdc`의 Planning Mode 규칙과 완전히 동일
- **대안**: `agent.mdc` 참조로 대체
- **삭제 후**: "Phase 번호 결정 기준은 `agent.mdc`의 Planning Mode 규칙을 따릅니다."로 간소화

#### `docs/` 역할 설명 (line 11-21)
- **이유**: `agent.mdc`에 이미 명시되어 있음
- **대안**: `agent.mdc` 참조로 대체
- **삭제 후**: "`docs/` 폴더의 역할은 `agent.mdc`의 Planning Mode 섹션을 참조하세요."로 간소화

---

### 2. `plan.mdc`에서 삭제 가능한 내용

#### Phase/Sub-task 추가/변경/삭제 시 (line 255-268)
- **이유**: `tasks.mdc`에 상세 프로세스가 이미 있음
- **대안**: `tasks.mdc` 참조로 대체
- **삭제 후**: "Phase/Sub-task 추가/변경/삭제 프로세스는 `tasks.mdc`를 참조하세요."로 간소화

#### 파일 명명 규칙 (line 146-151)
- **이유**: `tasks.mdc`에 동일한 내용이 있음
- **대안**: `tasks.mdc` 참조로 대체
- **삭제 후**: "`plan/tasks/` 파일 명명 규칙은 `tasks.mdc`를 참조하세요."로 간소화

#### `docs/` 역할 설명 (line 144)
- **이유**: `docs.mdc`에 상세 설명이 있음
- **대안**: `docs.mdc` 참조로 대체
- **삭제 후**: "`docs/` 디렉토리 역할은 `docs.mdc`를 참조하세요."로 간소화

---

### 3. `agent.mdc`에서 간소화 가능한 내용

#### `docs/` 역할 설명 (line 33)
- **이유**: `docs.mdc`에 더 상세한 설명이 있음
- **대안**: 간소화하고 `docs.mdc` 참조 추가
- **수정 후**: "역할: 구현 중 확인해야 할 내용, 대안 탐색, 질문에 대한 답변 등 (상세는 `docs.mdc` 참조)"

#### Phase/Sub-task 변경 시 일관성 유지 (line 15-24)
- **이유**: `tasks.mdc`에 상세 프로세스가 있음
- **대안**: 요약만 남기고 `tasks.mdc` 참조 추가
- **수정 후**: "Phase/Sub-task 변경 시 일관성 유지 프로세스는 `tasks.mdc`를 참조하세요."

---

### 4. `tasks.mdc`에서 중복 확인 필요

#### Phase 번호 체계 (line 30-32)
- **이유**: `agent.mdc`에 이미 명시되어 있음
- **대안**: `agent.mdc` 참조로 대체
- **삭제 후**: "Phase 번호 체계는 `agent.mdc`를 참조하세요."로 간소화

---

## 📋 권장 수정 사항 요약

### 즉시 수정 필요 (Critical)

1. **승인 프로세스 통일**: 모든 파일에서 `agent.mdc` 참조로 통일
2. **History 기록 형식 통일**: 모든 파일에서 동일한 형식 사용 또는 명확히 구분
3. **Phase/Sub-task 변경 프로세스 통일**: `tasks.mdc`에만 상세 내용, 다른 파일은 참조만

### 개선 권장 (Medium)

4. **Phase 번호 결정 기준**: `docs.mdc`에서 삭제하고 `agent.mdc` 참조
5. **파일 명명 규칙**: 각 파일에서 중복 제거, 해당 규칙 파일 참조로 통일
6. **Phase 번호 체계**: `agent.mdc`에만 명시, 다른 파일은 참조만
7. **`docs/` 역할 설명**: `agent.mdc`와 `plan.mdc`에서 간소화, `docs.mdc` 참조

### 참고 사항 (Minor)

8. **문서 동기화 우선순위**: 명확한 우선순위 정의
9. **역방향 동기화**: 명확한 규칙 정의

---

## 🔄 수정 우선순위

### 1단계: 승인 프로세스 통일
- 모든 파일에서 `agent.mdc`의 승인 규칙 참조로 통일
- `docs.mdc`의 "중요한 변경사항인 경우" 조건 명확화

### 2단계: History 기록 형식 통일
- 모든 파일에서 동일한 History 형식 사용
- 또는 모드별로 명확히 구분

### 3단계: 중복 내용 제거
- `docs.mdc`: Phase 번호 결정 기준 삭제, `agent.mdc` 참조
- `plan.mdc`: Phase/Sub-task 변경 프로세스 삭제, `tasks.mdc` 참조
- `tasks.mdc`: Phase 번호 체계 삭제, `agent.mdc` 참조

### 4단계: 문서 동기화 우선순위 명확화
- 단방향 동기화 규칙 정의
- 우선순위 명시

---

## 📅 작성일

2025-01-27

