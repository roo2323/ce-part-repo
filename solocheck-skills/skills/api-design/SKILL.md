---
name: api-design
description: RESTful API 엔드포인트 설계 시 사용. ARCHITECT 전용. URL, 메서드, 요청/응답 설계.
---

# API 엔드포인트 설계 체크리스트

## URL 규칙
- [ ] Base Path: `/api/v1`
- [ ] 리소스명 복수형 소문자 (`/users`, `/contacts`)
- [ ] kebab-case 사용 (`/check-in`, `/personal-message`)
- [ ] 계층 구조 명확 (`/users/{id}/contacts`)

## HTTP 메서드
- [ ] GET: 조회 (목록, 단일)
- [ ] POST: 생성
- [ ] PUT: 전체 수정
- [ ] PATCH: 부분 수정 (선택)
- [ ] DELETE: 삭제

## 요청/응답 규칙
- [ ] JSON Body는 snake_case
- [ ] 응답 형식 통일: `{ "data": ..., "meta": ... }`
- [ ] 에러 형식 통일: `{ "code": "...", "message": "..." }`

## 상태 코드
- [ ] 200: 조회/수정 성공
- [ ] 201: 생성 성공
- [ ] 204: 삭제 성공 (No Content)
- [ ] 400: 잘못된 요청
- [ ] 401: 인증 필요
- [ ] 403: 권한 없음
- [ ] 404: 리소스 없음
- [ ] 409: 충돌 (중복)
- [ ] 422: 검증 실패

---

## API 명세 템플릿
```markdown
### {METHOD} /api/v1/{resource}
{API 설명}

**인증**: 필요 / 불필요

**Request Body**:
```json
{
  "field1": "string (설명, 제약조건)",
  "field2": "integer (1-100)"
}
```

**Response {STATUS_CODE}**:
```json
{
  "id": "uuid",
  "field1": "value",
  "created_at": "2025-01-20T10:00:00Z"
}
```

**Error Cases**:
| 상황 | 코드 | HTTP |
|------|------|------|
| {상황} | {CODE001} | {400} |
```

---

## 완료 확인
- [ ] 모든 엔드포인트 정의
- [ ] 요청/응답 스키마 정의
- [ ] 에러 케이스 정의
- [ ] SPEC.md 업데이트
- [ ] BACKEND_DEV 인계 준비
