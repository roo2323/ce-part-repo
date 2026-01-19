---
name: task-review
description: 에이전트 작업 완료 검토 및 승인/반려 시 사용. ORCHESTRATOR 전용. 품질 관리.
---

# Task 완료 검토 체크리스트

## 검토 항목 - 공통
- [ ] SPEC.md 요구사항 충족 여부
- [ ] CLAUDE.md 규칙 준수 여부
- [ ] 예상 산출물 모두 제출됨
- [ ] 파일명/경로 규칙 준수

## 검토 항목 - 코드
- [ ] 코드 템플릿 준수 (해당 에이전트 문서 참조)
- [ ] Type Hints 적용 (Python)
- [ ] 타입 정의 적용 (TypeScript)
- [ ] 테스트 코드 포함 여부

## 검토 항목 - 문서
- [ ] 필수 섹션 포함
- [ ] 포맷 일관성
- [ ] 오타/문법 오류 없음

---

## 승인 시
```markdown
## [ORCHESTRATOR] 작업 검토 결과

**Task ID**: {Phase}-{Number}
**담당**: {AGENT}
**작업**: {작업 내용}

### 검토 항목
- [x] SPEC.md 요구사항 충족
- [x] CLAUDE.md 규칙 준수
- [x] 코드 품질 적합
- [x] 테스트 포함

### 결정: ✅ 승인

### 다음 단계
- {AGENT}: Task {X}-{Y} 시작 가능
```

---

## 반려 시
```markdown
## [ORCHESTRATOR] 작업 검토 결과

**Task ID**: {Phase}-{Number}
**담당**: {AGENT}

### 검토 항목
- [x] SPEC.md 요구사항 충족
- [ ] 코드 품질 적합 ← 미충족

### 결정: ❌ 반려

### 수정 요청
1. {구체적인 수정 사항}
2. {구체적인 수정 사항}

수정 후 다시 제출해주세요.
```
