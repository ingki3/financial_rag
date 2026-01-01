# 규칙 파일 문제점 분석

## 📋 개요

`agent.mdc`, `plan.mdc`, `prd.mdc` 세 규칙 파일을 검토한 결과, 프로젝트 진행 시 발생할 수 있는 문제점들을 정리했습니다.

---

## 🔴 심각한 문제점 (Critical Issues)

### 1. Phase 번호 체계 불일치 ✅ 해결됨

**문제점**:
- `agent.mdc` (line 13): "Phase 4-1", "Phase 5-2" 형식 언급
- `plan.mdc` (line 100): "N.1", "N.2", "N.3" 형식 언급
- 실제 `plan/plan.md`에서는 "Phase 5", "5.1", "5.2" 형식 사용

**영향**:
- AI가 Phase 번호를 어떻게 표기해야 할지 혼란스러울 수 있음
- 문서 간 일관성 부족

**해결 방안**:
- ✅ `agent.mdc`를 기준으로 Phase 번호 체계 통일: "Phase N" (메인 Phase), "N-M" (Sub-task, 하이픈 사용)
- ✅ `plan.mdc`의 모든 Sub-task 번호를 하이픈 형식으로 수정 완료
- ✅ `agent.mdc`의 Phase 번호 체계 설명을 더 명확하게 수정 완료

---

### 2. 파일 명명 규칙 불일치 ✅ 해결됨

**문제점**:
- `agent.mdc` (line 23): `docs/{Phase numbering}-{problem to solve}.md`
  - 예: `docs/5-1-normalization-improvement.md`
- `plan.mdc` (line 144-148): `plan/tasks/phase-{N}/phase-{N}.md`, `phase-{N}-{M}.md`
  - 예: `plan/tasks/phase-5/phase-5-1.md`

**영향**:
- `docs/`와 `plan/tasks/` 디렉토리의 역할이 중복될 수 있음
- 파일 이름 형식이 다르면 혼란 발생

**해결 방안**:
- ✅ 역할 명확화:
  - **`docs/`**: 구현 중 확인해야 할 내용, 대안 탐색, 질문에 대한 답변 등. 즉, 바로 계획에 반영되지 않고, 중간에 확인할 정보, 대안 탐색, 현재 상태 확인 등에 대한 기록
  - **`plan/tasks/`**: 실제 구현을 위한 계획 및 정보. 실제 구현에 반영된 또는 반영될 내용
- 역할을 명확히 구분하고, 파일 명명 규칙을 통일

---

### 3. History 기록 위치 모호성 ✅ 해결됨

**문제점**:
- `agent.mdc` (line 26-27): `plan/tasks/phase-{N}/phase-{N}-{M}.md` **또는** `phase-{N}.md` 중 어디에 기록할지 모호
- Planning Mode와 Implementation Mode 모두에서 History를 기록하지만, 어떤 파일에 기록할지 기준이 없음

**영향**:
- AI가 History를 어디에 기록해야 할지 판단하기 어려움
- History가 여러 파일에 분산되거나 누락될 수 있음

**해결 방안**:
- ✅ 모든 History를 `phase-{N}.md`에 통합 기록하도록 명확히 정의
- ✅ Planning Mode와 Implementation Mode 모두에서 `plan/tasks/phase-{N}/phase-{N}.md` 파일에 기록하도록 수정 완료

---

### 4. Phase 번호 결정 기준 모호 ✅ 해결됨

**문제점**:
- `agent.mdc` (line 39, 67): "Determine the appropriate `plan/tasks/phase-{N}/` file based on the Phase number"
- 하지만 Planning Mode에서 생성하는 문서의 Phase 번호를 어떻게 결정할지 명확하지 않음
- 사용자가 명시하지 않으면 AI가 임의로 결정해야 함

**영향**:
- 잘못된 Phase 번호로 파일이 생성될 수 있음
- 문서 간 연결이 끊어질 수 있음

**해결 방안**:
- ✅ Planning Mode에서 Phase 번호를 결정하는 명확한 기준을 `agent.mdc`에 추가:
  1. **사용자가 명시한 경우**: 그대로 사용
  2. **사용자가 명시하지 않은 경우**: 
     - 관련된 기존 Phase를 찾아서 사용 (예: 정규화 관련 문제 → Phase 4 관련)
     - 관련 Phase가 없으면 새로운 Phase 번호로 생성하거나 사용자에게 확인 요청
  3. **불명확한 경우**: 사용자에게 Phase 번호 확인 요청

---

## 🟡 중간 수준 문제점 (Medium Issues)

### 5. 승인 프로세스 중복 및 불일치

**문제점**:
- `agent.mdc` (line 14): `plan/prd.md` 또는 `plan/plan.md` 수정 전 승인 필요
- `plan.mdc` (line 15): `plan/plan.md` 수정 전 승인 필요
- `prd.mdc` (line 15): `plan/prd.md` 수정 전 승인 필요

**영향**:
- 세 문서 모두에서 승인 규칙이 언급되어 있지만, 실제로는 `agent.mdc`의 규칙이 우선 적용됨
- 중복된 규칙으로 인한 혼란 가능성

**해결 방안**:
- 승인 프로세스를 `agent.mdc`에만 명시하고, `plan.mdc`와 `prd.mdc`에서는 참조만 하도록 수정

---

### 6. 문서 동기화 책임 불명확

**문제점**:
- `plan.mdc` (line 16-18): `plan/plan.md` 수정 시 연관 문서 확인 필요
- `agent.mdc`에는 문서 동기화 규칙이 없음
- AI가 `plan/plan.md`를 수정할 때 동기화를 자동으로 수행해야 하는지 불명확

**영향**:
- 문서 간 불일치 발생 가능
- 동기화 누락 가능

**해결 방안**:
- `agent.mdc`에 문서 동기화 규칙 추가:
  - `plan/plan.md` 수정 시 `plan/prd.md`와 `plan/tasks/` 확인
  - `plan/prd.md` 수정 시 `plan/plan.md` 확인

---

### 7. Planning Mode와 Implementation Mode 경계 모호

**문제점**:
- `agent.mdc` (line 18-19): "계획을 세워달라" → Planning Mode
- `agent.mdc` (line 41-42): "코딩해달라" → Implementation Mode
- 하지만 "계획도 세우고 코드도 작성해달라" 같은 요청은 어떻게 처리할지 불명확

**영향**:
- AI가 모드를 잘못 판단할 수 있음
- 사용자 의도와 다르게 동작할 수 있음

**해결 방안**:
- 복합 요청 처리 규칙 추가:
  - 계획 + 구현 요청: 먼저 Planning Mode로 계획 문서 생성, 그 다음 Implementation Mode로 구현
  - 불명확한 경우: 사용자에게 확인

---

### 8. History 날짜 형식 표준화 부재

**문제점**:
- `agent.mdc` (line 32): `{Date}` 형식만 명시
- 날짜 형식 (YYYY-MM-DD, YYYY/MM/DD 등)이 명시되지 않음

**영향**:
- 일관성 없는 날짜 형식 사용 가능
- History 검색 및 추적 어려움

**해결 방안**:
- 날짜 형식을 명확히 정의: `YYYY-MM-DD` 형식 사용

---

### 9. docs/와 plan/tasks/ 역할 중복

**문제점**:
- `agent.mdc` (line 22): Planning Mode에서 `docs/`에 계획 문서 생성
- `plan.mdc` (line 132): `plan/tasks/`에 상세 구현 문서 작성
- 두 디렉토리의 역할이 명확히 구분되지 않음

**영향**:
- 문서가 어디에 저장되어야 할지 혼란
- 중복 저장 가능성

**해결 방안**:
- 역할 명확화:
  - `docs/`: Planning Mode에서 생성하는 **문제 해결 계획 문서** (일회성, 특정 문제 해결용)
  - `plan/tasks/`: **상세 구현 문서** (Phase별 구현 가이드, 지속적 관리)

---

### 10. plan/tasks 파일 존재 여부 확인 프로세스 불명확

**문제점**:
- `agent.mdc` (line 38, 66): "If the plan/tasks file doesn't exist: Create it first"
- 하지만 파일이 존재하는지 확인하는 프로세스가 명시되지 않음
- 파일이 존재하지만 History 섹션이 없는 경우 처리 방법 불명확

**영향**:
- History 섹션을 추가해야 하는데 파일을 새로 생성할 수 있음
- 기존 파일을 덮어쓸 위험

**해결 방안**:
- 파일 존재 여부 확인 프로세스 명시:
  1. 파일 존재 확인
  2. 존재하면 History 섹션 추가/업데이트
  3. 존재하지 않으면 파일 생성 후 History 섹션 추가

---

## 🟢 경미한 문제점 (Minor Issues)

### 11. Phase 번호 참조 방식 불일치

**문제점**:
- `agent.mdc`: "Phase 4-1" 형식 사용
- `plan.mdc`: "Phase N", "N.1" 형식 사용
- 실제 `plan/plan.md`: "Phase 5", "5.1" 형식 사용

**해결 방안**:
- 모든 문서에서 "Phase N", "N.M" 형식으로 통일

---

### 12. 파일 경로 표기법 불일치

**문제점**:
- `agent.mdc`: `plan/tasks/phase-{N}/` 형식
- `plan.mdc`: `plan/tasks/phase-{N}/` 형식 (일치)
- 하지만 실제 사용 시 대소문자, 하이픈 사용이 일관되지 않을 수 있음

**해결 방안**:
- 파일 경로 표기법을 명확히 정의하고 예시 제공

---

## 📝 권장 수정 사항 요약

### 즉시 수정 필요 (Critical)

1. **Phase 번호 체계 통일**: ✅ 완료 - `agent.mdc` 기준으로 "Phase N", "N-M" 형식으로 통일
2. **파일 명명 규칙 통일**: ✅ 완료 - `docs/`와 `plan/tasks/` 역할 명확화
3. **History 기록 위치 명확화**: ✅ 완료 - 모든 History를 `phase-{N}.md`에 통합 기록하도록 명확히 정의
4. **Phase 번호 결정 기준 명확화**: ✅ 완료 - Planning Mode에서 Phase 번호 결정 기준을 명확히 정의

### 개선 권장 (Medium)

5. **승인 프로세스 정리**: 중복 제거 및 명확화
6. **문서 동기화 규칙 추가**: `agent.mdc`에 동기화 규칙 추가
7. **모드 경계 명확화**: 복합 요청 처리 규칙 추가
8. **날짜 형식 표준화**: YYYY-MM-DD 형식 명시
9. **파일 존재 확인 프로세스 명시**: 단계별 프로세스 정의

### 참고 사항 (Minor)

10. **파일 경로 표기법 통일**: 예시 제공
11. **용어 통일**: 모든 문서에서 동일한 용어 사용

---

## ✅ 수정 완료 사항

### 2025-01-27
- ✅ Phase 번호 체계 통일: `agent.mdc`를 기준으로 "Phase N", "N-M" (하이픈) 형식으로 통일
  - `plan.mdc`의 모든 Sub-task 번호 표기를 점(.)에서 하이픈(-)으로 변경
  - `agent.mdc`의 Phase 번호 체계 설명을 더 명확하게 수정
- ✅ History 기록 위치 명확화: 모든 History를 `phase-{N}.md`에 통합 기록하도록 명확히 정의
  - Planning Mode와 Implementation Mode 모두에서 `plan/tasks/phase-{N}/phase-{N}.md` 파일에 기록하도록 수정
  - 모호한 "또는" 표현을 제거하고 단일 파일로 명확히 지정
- ✅ 파일 명명 규칙 통일: `docs/`와 `plan/tasks/` 역할 명확화
  - `docs/`: 구현 중 확인해야 할 내용, 대안 탐색, 질문에 대한 답변 등. 즉, 바로 계획에 반영되지 않고, 중간에 확인할 정보, 대안 탐색, 현재 상태 확인 등에 대한 기록
  - `plan/tasks/`: 실제 구현을 위한 계획 및 정보. 실제 구현에 반영된 또는 반영될 내용
  - `agent.mdc`와 `plan.mdc`에 역할 정의 추가
- ✅ Phase 번호 결정 기준 명확화: Planning Mode에서 Phase 번호 결정 기준을 `agent.mdc`에 추가
  - 사용자가 명시한 경우: 그대로 사용
  - 사용자가 명시하지 않은 경우: 관련된 기존 Phase를 찾거나, 새로운 Phase로 생성하거나 사용자에게 확인 요청
  - 불명확한 경우: 사용자에게 Phase 번호 확인 요청
- ✅ Tasks 문서 동기화 규칙 생성: `tasks.mdc` 파일 생성
  - `plan/tasks/**/*.md` 파일에 적용되도록 설정
  - `plan/tasks/` 하부 파일 수정 시 `plan/plan.md`와 `plan/prd.md` 동기화 프로세스 정의
  - 동기화 체크리스트 및 History 기록 규칙 포함
- ✅ Phase/Sub-task 변경 시 일관성 유지 규칙 추가
  - `agent.mdc`에 Phase/Sub-task 변경 시 전체 문서 동기화 규칙 추가
  - `tasks.mdc`에 Phase/Sub-task 추가/변경/삭제 상세 프로세스 추가:
    - Phase 추가/삭제/번호 변경 프로세스
    - Sub-task 추가/삭제/번호 변경 프로세스
    - 번호 재정렬 프로세스
    - 파일/폴더 이름 변경 규칙
    - 참조 업데이트 규칙
  - `plan.mdc`에 Phase/Sub-task 변경 프로세스 참조 추가

---

## 🔍 추가 검토 필요 사항

1. **에러 처리**: 규칙을 따를 수 없는 상황에서의 처리 방법
2. **역방향 호환성**: ✅ 해결됨 - `tasks.mdc` 파일 생성으로 `plan/tasks/` 하부 파일 수정 시 `plan/plan.md`와 `plan/prd.md` 동기화 규칙 정의
3. **확장성**: ✅ 해결됨 - `tasks.mdc`에 새로운 Phase나 Sub-task 추가 시 규칙 적용 방법 명시
4. **Phase/Sub-task 변경 시 일관성 유지**: ✅ 해결됨 - Phase나 Sub-task 추가/변경/삭제 시 일관성 유지 프로세스 정의
   - `agent.mdc`에 Phase/Sub-task 변경 시 전체 문서 동기화 규칙 추가
   - `tasks.mdc`에 Phase/Sub-task 추가/변경/삭제 상세 프로세스 추가
   - `plan.mdc`에 Phase/Sub-task 변경 프로세스 참조 추가
5. **자동화 가능성**: 일부 규칙을 자동으로 검증할 수 있는 방법

## 🤖 자동화 가능한 검증 방법 제안

다음과 같은 검증 스크립트나 도구를 개발하여 규칙 준수를 자동으로 확인할 수 있습니다:

### 1. Phase 번호 형식 검증

**검증 항목**:
- `plan/plan.md`에서 Phase 제목이 "Phase N" 형식인지 확인
- Sub-task 제목이 "N-M" 형식(하이픈 사용)인지 확인
- 잘못된 형식(예: "Phase 4-1", "5.1") 사용 시 경고

**구현 방법**:
```python
# scripts/validate_phase_numbering.py
import re
from pathlib import Path

def validate_phase_format(content):
    # Phase 제목 검증: "## Phase N:" 형식
    phase_pattern = r'^## Phase (\d+):'
    # Sub-task 제목 검증: "### N-M" 형식 (점 사용 금지)
    subtask_pattern = r'^### (\d+)-(\d+)'
    # 잘못된 형식 검출
    invalid_patterns = [
        r'Phase \d+-\d+',  # "Phase 4-1" 형식 금지
        r'### \d+\.\d+',   # "5.1" 형식 금지
    ]
    # 검증 로직...
```

### 2. 파일 구조 일치 검증

**검증 항목**:
- `plan/plan.md`에 정의된 Phase가 `plan/tasks/phase-{N}/` 폴더와 일치하는지 확인
- `plan/plan.md`의 Sub-task N-M이 `plan/tasks/phase-{N}/phase-{N}-{M}.md` 파일과 일치하는지 확인
- 누락된 파일이나 폴더 감지
- 불필요한 파일이나 폴더 감지

**구현 방법**:
```python
# scripts/validate_file_structure.py
def validate_file_structure():
    # plan.md에서 Phase와 Sub-task 추출
    phases_in_plan = extract_phases_from_plan_md()
    # tasks/ 폴더 구조 확인
    tasks_folders = list_tasks_folders()
    
    # 일치 여부 확인
    for phase_num in phases_in_plan:
        expected_folder = f"plan/tasks/phase-{phase_num}/"
        if expected_folder not in tasks_folders:
            print(f"⚠️ Missing folder: {expected_folder}")
    
    # Sub-task 파일 확인
    for phase_num, subtasks in phases_in_plan.items():
        for subtask_num in subtasks:
            expected_file = f"plan/tasks/phase-{phase_num}/phase-{phase_num}-{subtask_num}.md"
            if not Path(expected_file).exists():
                print(f"⚠️ Missing file: {expected_file}")
```

### 3. 문서 간 Phase 번호 참조 일치 검증

**검증 항목**:
- `plan/plan.md`에서 언급된 Phase 번호가 `plan/prd.md`의 FR-XX와 매핑되는지 확인
- `docs/` 폴더의 문서에서 Phase 번호 참조가 올바른지 확인
- `plan/tasks/` 파일 내부의 Phase 번호 참조가 일치하는지 확인

**구현 방법**:
```python
# scripts/validate_cross_references.py
def validate_cross_references():
    # plan.md에서 Phase 추출
    phases_in_plan = extract_phases_from_plan_md()
    
    # prd.md에서 FR-XX와 Phase 매핑 확인
    fr_phase_mapping = extract_fr_phase_mapping_from_prd()
    
    # docs/ 폴더의 문서에서 Phase 번호 참조 확인
    docs_files = list_docs_files()
    for doc_file in docs_files:
        phase_refs = extract_phase_refs_from_file(doc_file)
        for ref in phase_refs:
            if ref not in phases_in_plan:
                print(f"⚠️ Invalid Phase reference in {doc_file}: {ref}")
```

### 4. History 기록 형식 검증

**검증 항목**:
- `plan/tasks/phase-{N}/phase-{N}.md` 파일에 History 섹션이 있는지 확인
- History 항목이 올바른 형식인지 확인 (날짜, 요약, 상태 등)
- History가 `phase-{N}.md`에만 기록되고 `phase-{N}-{M}.md`에는 없는지 확인

**구현 방법**:
```python
# scripts/validate_history_format.py
def validate_history_format():
    history_pattern = r'## 📝 History\s+### (\d{4}-\d{2}-\d{2})'
    required_fields = [
        'User Request',
        'Modified/Created Files',
        'Purpose',
        'Status'
    ]
    
    for phase_file in list_phase_files():
        content = read_file(phase_file)
        if not re.search(history_pattern, content):
            print(f"⚠️ Missing History section in {phase_file}")
        
        # History 항목 형식 검증
        history_entries = extract_history_entries(content)
        for entry in history_entries:
            for field in required_fields:
                if field not in entry:
                    print(f"⚠️ Missing field '{field}' in {phase_file}")
```

### 5. Phase/Sub-task 번호 연속성 검증

**검증 항목**:
- Phase 번호가 연속적으로 존재하는지 확인 (1, 2, 3, ...)
- 각 Phase의 Sub-task 번호가 연속적으로 존재하는지 확인 (N-1, N-2, N-3, ...)
- 번호가 건너뛰어져 있는지 확인

**구현 방법**:
```python
# scripts/validate_numbering_continuity.py
def validate_numbering_continuity():
    phases = sorted(extract_phase_numbers())
    
    # Phase 번호 연속성 확인
    for i in range(len(phases) - 1):
        if phases[i+1] - phases[i] != 1:
            print(f"⚠️ Phase numbering gap: {phases[i]} -> {phases[i+1]}")
    
    # Sub-task 번호 연속성 확인
    for phase_num in phases:
        subtasks = sorted(extract_subtask_numbers(phase_num))
        for i in range(len(subtasks) - 1):
            if subtasks[i+1] - subtasks[i] != 1:
                print(f"⚠️ Sub-task numbering gap in Phase {phase_num}: {subtasks[i]} -> {subtasks[i+1]}")
```

### 6. 통합 검증 스크립트

**구현 방법**:
```python
# scripts/validate_all_rules.py
"""
프로젝트 규칙 준수 여부를 종합적으로 검증하는 스크립트
"""
from pathlib import Path
import sys

def main():
    errors = []
    warnings = []
    
    # 1. Phase 번호 형식 검증
    errors.extend(validate_phase_format())
    
    # 2. 파일 구조 일치 검증
    errors.extend(validate_file_structure())
    
    # 3. 문서 간 참조 일치 검증
    errors.extend(validate_cross_references())
    
    # 4. History 기록 형식 검증
    warnings.extend(validate_history_format())
    
    # 5. 번호 연속성 검증
    warnings.extend(validate_numbering_continuity())
    
    # 결과 출력
    if errors:
        print("❌ Errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    if warnings:
        print("⚠️ Warnings found:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("✅ All validations passed!")

if __name__ == "__main__":
    main()
```

### 7. Git Hook 통합

**구현 방법**:
- Pre-commit hook에 검증 스크립트 추가
- 커밋 전 자동으로 규칙 검증 수행
- 검증 실패 시 커밋 차단

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/validate_all_rules.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Please fix the issues before committing."
    exit 1
fi
```

### 8. CI/CD 파이프라인 통합

**구현 방법**:
- GitHub Actions, GitLab CI 등에 검증 단계 추가
- Pull Request 생성 시 자동 검증
- 검증 결과를 PR 코멘트로 표시

```yaml
# .github/workflows/validate-rules.yml
name: Validate Project Rules

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Validate rules
        run: python scripts/validate_all_rules.py
```

### 9. IDE 플러그인/확장 기능

**구현 방법**:
- VS Code/Cursor 확장 기능 개발
- 문서 편집 시 실시간 검증
- 문제 발견 시 인라인 경고 표시

### 10. 문서 생성 자동화

**구현 방법**:
- Phase/Sub-task 추가 시 필요한 파일 자동 생성
- 템플릿 기반 문서 생성
- 기본 구조 자동 생성

```python
# scripts/generate_phase_structure.py
def generate_phase_structure(phase_num, phase_name):
    # plan/plan.md에 Phase 섹션 추가
    add_phase_to_plan_md(phase_num, phase_name)
    
    # plan/tasks/phase-{N}/ 폴더 생성
    create_tasks_folder(phase_num)
    
    # phase-{N}.md 파일 생성 (템플릿 사용)
    create_phase_md_file(phase_num, phase_name)
    
    # 기본 History 섹션 추가
    add_history_section(phase_num)
```

## 📋 우선순위 제안

1. **높은 우선순위**: Phase 번호 형식 검증, 파일 구조 일치 검증
2. **중간 우선순위**: 문서 간 참조 일치 검증, History 기록 형식 검증
3. **낮은 우선순위**: 번호 연속성 검증, Git Hook 통합
4. **향후 고려**: CI/CD 통합, IDE 플러그인, 문서 생성 자동화

## 💡 추가 고려사항

- **점진적 도입**: 모든 검증을 한 번에 구현하기보다는 단계적으로 도입
- **사용자 피드백**: 검증 규칙이 너무 엄격하면 개발 흐름을 방해할 수 있으므로 조정 필요
- **성능 고려**: 대규모 프로젝트에서 검증 시간 최소화
- **오탐 최소화**: 정규식 패턴을 정확하게 설계하여 오탐 최소화

---

## 📅 작성일

2025-01-27

