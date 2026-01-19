---
name: bug-report
description: 버그 리포트 작성 시 사용. QA 전용. 버그 문서화 및 추적.
---

# 버그 리포트 체크리스트

## 필수 항목
- [ ] 버그 ID
- [ ] 제목 (간결하고 명확하게)
- [ ] 심각도 (Critical/High/Medium/Low)
- [ ] 재현 단계
- [ ] 예상 결과
- [ ] 실제 결과

## 선택 항목
- [ ] 스크린샷/로그
- [ ] 환경 정보
- [ ] 관련 코드 위치
- [ ] 담당자

## 심각도 기준
| 심각도 | 기준 |
|--------|------|
| 🔴 Critical | 시스템 다운, 데이터 손실 |
| 🟠 High | 핵심 기능 불가 |
| 🟡 Medium | 기능 제한, 우회 가능 |
| 🟢 Low | UI 이슈, 사소한 문제 |

---

## 버그 리포트 템플릿
```markdown
## [BUG] {버그 ID}: {제목}

**심각도**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
**상태**: 🔵 Open / 🟢 Fixed / 🔴 Rejected
**발견일**: {YYYY-MM-DD}
**담당**: {에이전트 또는 담당자}

### 재현 단계
1. {첫 번째 단계}
2. {두 번째 단계}
3. {세 번째 단계}

### 예상 결과
{정상적으로 동작해야 하는 방식}

### 실제 결과
{실제로 발생한 문제}

### 환경
- OS: {운영체제}
- Python: {버전}
- 브랜치: {브랜치명}

### 로그/스크린샷
```
{에러 로그}
```

### 관련 코드
- 파일: `src/{module}/{file}.py`
- 함수: `{function_name}`

### 메모
{추가 정보}
```

---

## 버그 리포트 예시
```markdown
## [BUG] BUG-001: 비상연락처 4번째 등록 시 서버 500 에러

**심각도**: 🟠 High
**상태**: 🔵 Open
**발견일**: 2025-01-20
**담당**: BACKEND_DEV

### 재현 단계
1. 로그인
2. 비상연락처 3개 등록
3. 4번째 연락처 등록 시도

### 예상 결과
400 Bad Request, 에러 코드 "CONTACT001" 반환

### 실제 결과
500 Internal Server Error

### 로그
```
sqlalchemy.exc.IntegrityError: (psycopg2.IntegrityError) 
duplicate key value violates unique constraint
```

### 관련 코드
- 파일: `src/contacts/service.py`
- 함수: `create_contact`
```

---

## 완료 확인
- [ ] 필수 항목 모두 작성
- [ ] 재현 가능한 단계 명시
- [ ] 심각도 적절히 분류
- [ ] ORCHESTRATOR에게 보고
