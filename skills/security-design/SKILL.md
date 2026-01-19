---
name: security-design
description: 보안 아키텍처 설계 시 사용. ARCHITECT 전용. 인증, 암호화, 접근제어 설계.
---

# 보안 아키텍처 설계 체크리스트

## 인증 (Authentication)
- [ ] JWT 기반 인증 사용
- [ ] Access Token 만료 시간 설정 (15분 권장)
- [ ] Refresh Token 만료 시간 설정 (7일 권장)
- [ ] 토큰 서명 알고리즘 명시 (HS256)

## 비밀번호 보안
- [ ] bcrypt 해싱 사용
- [ ] cost factor 설정 (12 권장)
- [ ] 최소 비밀번호 길이 정의 (8자 이상)

## 민감 데이터 암호화
- [ ] 암호화 대상 데이터 식별
- [ ] AES-256-GCM 사용
- [ ] 암호화 키 관리 방안 명시
- [ ] 키 로테이션 정책 (선택)

## 통신 보안
- [ ] HTTPS 필수
- [ ] CORS 설정 명시
- [ ] Rate Limiting 정책 정의

---

## JWT 토큰 구조
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "type": "access | refresh"
}
```

## Rate Limiting 정책
| 엔드포인트 | 제한 |
|------------|------|
| POST /auth/login | 5회/분 |
| POST /auth/register | 3회/분 |
| 기타 인증 필요 API | 100회/분 |
| 기타 공개 API | 30회/분 |

## 암호화 대상
| 데이터 | 방식 | 알고리즘 |
|--------|------|----------|
| 비밀번호 | 해싱 | bcrypt |
| 개인 메시지 | 암호화 | AES-256-GCM |
| JWT | 서명 | HS256 |

---

## 완료 확인
- [ ] 인증 플로우 설계 완료
- [ ] 암호화 명세 완료
- [ ] Rate Limiting 정책 정의
- [ ] SPEC.md 업데이트
- [ ] BACKEND_DEV 인계 준비
