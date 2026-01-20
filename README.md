# SoloCheck (솔로체크)

> 혼자 사는 사용자의 장기 미연락 상황을 감지하여, 사전 지정된 연락처에 자동 알림과 개인 메시지를 전달하는 모바일 서비스

## 핵심 가치

| 원칙 | 설명 |
|------|------|
| **비침습적** | 사망 여부를 판단하지 않음 |
| **프라이버시 우선** | 최소 정보 수집, 암호화 저장 |
| **법적 안전성** | 윤리적·법적 책임 최소화 설계 |
| **단순함** | 복잡한 기능보다 확실한 핵심 기능 |

## 프로젝트 구조

```
solocheck/
├── solocheck-app/        # React Native 앱 (Expo)
├── solocheck-backend/    # FastAPI 백엔드
├── CLAUDE.md             # 프로젝트 헌법 (에이전트 규칙)
├── SPEC.md               # 상세 요구사항 명세
└── PROMPT_PLAN.md        # 단계별 실행 계획
```

## 기술 스택

### Frontend (solocheck-app)

| 구분 | 기술 |
|------|------|
| Framework | React Native + Expo SDK 51 |
| Language | TypeScript |
| State | Zustand |
| Navigation | Expo Router |
| HTTP Client | Axios |
| Form | react-hook-form + zod |

### Backend (solocheck-backend)

| 구분 | 기술 |
|------|------|
| Framework | FastAPI |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 15 |
| Queue | Celery + Redis |
| Auth | JWT (python-jose) |
| Email | SendGrid |
| Push | Firebase Cloud Messaging |

## 시작하기

### 사전 요구사항

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Expo CLI (`npm install -g expo-cli`)

### 백엔드 실행

```bash
cd solocheck-backend

# 환경 변수 설정
cp .env.example .env

# Docker로 실행 (PostgreSQL, Redis 포함)
docker compose up -d

# 데이터베이스 마이그레이션
docker exec solocheck-backend alembic upgrade head
```

백엔드 API: http://localhost:8000
API 문서: http://localhost:8000/docs

### 프론트엔드 실행

```bash
cd solocheck-app

# 의존성 설치
npm install

# 개발 서버 실행
npx expo start
```

- `w` - 웹 브라우저에서 열기
- `i` - iOS 시뮬레이터에서 열기
- `a` - Android 에뮬레이터에서 열기

## 주요 기능

### 1. 체크인 시스템
- 사용자가 주기적으로 앱에서 체크인
- 설정 가능한 체크인 주기 (7일, 14일, 30일)
- 유예 기간 설정 (24시간, 48시간, 72시간)

### 2. 비상연락처 관리
- 최대 3명의 비상연락처 등록
- 이메일 또는 SMS 알림 선택
- 우선순위 설정

### 3. 개인 메시지
- 비상시 전달될 개인 메시지 작성
- 암호화 저장

### 4. 자동 알림
- 체크인 미이행 시 자동 알림 발송
- 단계별 알림 (리마인더 → 비상연락처 알림)

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/auth/register` | 회원가입 |
| POST | `/api/v1/auth/login/json` | 로그인 |
| POST | `/api/v1/checkin` | 체크인 |
| GET | `/api/v1/contacts` | 연락처 목록 |
| POST | `/api/v1/contacts` | 연락처 추가 |
| GET | `/api/v1/message` | 개인 메시지 조회 |
| PUT | `/api/v1/message` | 개인 메시지 수정 |

## 서비스 고지

```
본 서비스는 사망 여부를 확인하지 않습니다.
긴급 상황 시 112/119 등 공공기관에 연락하세요.
알림은 '연락 두절' 기준으로 발송됩니다.
```

## 라이선스

Private - All rights reserved
