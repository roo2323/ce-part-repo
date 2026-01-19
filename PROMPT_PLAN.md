# PROMPT_PLAN.md - SoloCheck 단계별 실행 지시서

> 이 문서는 각 Phase별 작업 내용과 에이전트별 실행 프롬프트를 정의합니다.

---

## 📋 전체 로드맵

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 0: 프로젝트 셋업                        │
│  ▶ 레포지토리 초기화, 개발 환경 구성, Docker 설정                      │
│  ⏱ 예상: 0.5일                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: 기본 구조                           │
│  ▶ 인증/인가, 사용자 프로필, 체크인 주기 설정                          │
│  ⏱ 예상: 2일                                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: 핵심 로직                           │
│  ▶ 체크인 기록, 미체크 감지, 알림 발송                                │
│  ⏱ 예상: 3일                                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: 안정화                              │
│  ▶ 알림 템플릿, 예외 처리, 약관/고지, 테스트                          │
│  ⏱ 예상: 2일                                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 4: 릴리즈 준비                          │
│  ▶ 최종 테스트, 문서화, 빌드 설정                                     │
│  ⏱ 예상: 1일                                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 PHASE 0: 프로젝트 셋업

### 목표
- 두 개의 레포지토리 초기화
- 개발 환경 Docker 구성
- 기본 프로젝트 구조 생성

### 에이전트별 작업

---

#### 🎯 ORCHESTRATOR 지시

```markdown
## Phase 0 시작

목표: 프로젝트 기반 환경 구성

작업 순서:
1. ARCHITECT → 프로젝트 구조 정의 확인
2. BACKEND DEV → solocheck-backend 레포 초기화 (FastAPI)
3. FRONTEND DEV → solocheck-app 레포 초기화 (Expo)

완료 조건:
- [ ] Backend: FastAPI 프로젝트 생성, Docker Compose 작동
- [ ] App: Expo 프로젝트 생성, 기본 실행 확인
- [ ] 양쪽 레포 README.md 작성
```

---

#### ⚙️ BACKEND DEV 작업

**Task 0-1: Backend 프로젝트 초기화**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: solocheck-backend 프로젝트 초기화 (FastAPI + Python)

수행 내용:
1. 프로젝트 디렉토리 생성
   ```bash
   mkdir solocheck-backend
   cd solocheck-backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. 필수 패키지 설치 (requirements.txt)
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   sqlalchemy==2.0.25
   alembic==1.13.1
   psycopg2-binary==2.9.9
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   pydantic==2.5.3
   pydantic-settings==2.1.0
   celery==5.3.6
   redis==5.0.1
   firebase-admin==6.3.0
   sendgrid==6.11.0
   python-multipart==0.0.6
   httpx==0.26.0
   pytest==7.4.4
   pytest-asyncio==0.23.3
   ```

3. 기본 디렉토리 구조 생성
   ```
   src/
   ├── __init__.py
   ├── main.py
   ├── config.py
   ├── database.py
   ├── auth/
   ├── users/
   ├── checkin/
   ├── contacts/
   ├── messages/
   ├── notifications/
   ├── scheduler/
   └── common/
   alembic/
   tests/
   ```

4. Docker Compose 생성 (docker-compose.yml)
   ```yaml
   version: '3.8'
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_USER: solocheck
         POSTGRES_PASSWORD: solocheck
         POSTGRES_DB: solocheck
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"

     backend:
       build: .
       ports:
         - "8000:8000"
       depends_on:
         - db
         - redis
       environment:
         - DATABASE_URL=postgresql://solocheck:solocheck@db:5432/solocheck
         - REDIS_URL=redis://redis:6379/0
       volumes:
         - .:/app

   volumes:
     postgres_data:
   ```

5. 환경 변수 설정 (.env.example)
   ```
   DATABASE_URL=postgresql://solocheck:solocheck@localhost:5432/solocheck
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key-here
   FCM_CREDENTIALS_PATH=./firebase-credentials.json
   SENDGRID_API_KEY=your-sendgrid-api-key
   ```

6. FastAPI 기본 앱 설정 (src/main.py)
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(
       title="SoloCheck API",
       version="1.0.0",
       description="1인 가구 안부 확인 서비스"
   )
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   @app.get("/health")
   def health_check():
       return {"status": "ok"}
   ```

산출물:
- 실행 가능한 FastAPI 프로젝트
- docker-compose.yml
- README.md (실행 방법 포함)

완료 보고 형식으로 결과 제출
```

---

#### 📱 FRONTEND DEV 작업

**Task 0-2: App 프로젝트 초기화**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: solocheck-app 프로젝트 초기화

수행 내용:
1. Expo 프로젝트 생성
   ```bash
   npx create-expo-app solocheck-app -t expo-template-blank-typescript
   cd solocheck-app
   ```

2. 필수 패키지 설치
   ```bash
   npx expo install expo-router expo-linking expo-constants expo-status-bar
   npx expo install expo-notifications expo-device
   npx expo install @react-native-async-storage/async-storage
   npm install zustand axios
   npm install react-hook-form zod @hookform/resolvers
   ```

3. Expo Router 설정
   - app.json 수정
   - 기본 라우팅 구조 생성

4. 기본 디렉토리 구조 생성
   ```
   app/
   ├── (auth)/
   │   ├── login.tsx
   │   ├── register.tsx
   │   └── _layout.tsx
   ├── (tabs)/
   │   ├── home.tsx
   │   ├── contacts.tsx
   │   ├── message.tsx
   │   ├── settings.tsx
   │   └── _layout.tsx
   ├── _layout.tsx
   └── index.tsx
   components/
   services/
   stores/
   hooks/
   types/
   constants/
   utils/
   ```

5. 환경 변수 설정 (app.config.js)
   - API_URL 등

산출물:
- 실행 가능한 Expo 프로젝트
- 기본 네비게이션 구조
- README.md (실행 방법 포함)

완료 보고 형식으로 결과 제출
```

---

## 🔐 PHASE 1: 기본 구조

### 목표
- 사용자 인증 시스템 완성
- 체크인 주기 설정 기능
- 기본 UI 구현

### 에이전트별 작업

---

#### 🎯 ORCHESTRATOR 지시

```markdown
## Phase 1 시작

목표: 인증 및 기본 사용자 기능 구현

의존성 그래프:
```
ARCHITECT (DB 스키마)
       │
       ├──▶ BACKEND DEV (Auth API)
       │           │
       │           ▼
       └──▶ FRONTEND DEV (Auth UI) ◀── BACKEND DEV 완료 후
```

작업 순서:
1. ARCHITECT → SQLAlchemy 모델 & Alembic 마이그레이션
2. BACKEND DEV → Auth 모듈, User 모듈 구현
3. FRONTEND DEV → 로그인/회원가입 화면, 홈 화면

완료 조건:
- [ ] 회원가입 → 로그인 → 토큰 발급 플로우 작동
- [ ] 체크인 주기 설정 및 조회 가능
- [ ] 앱에서 로그인 후 홈 화면 진입
```

---

#### 🏗️ ARCHITECT 작업

**Task 1-1: DB 스키마 적용**

```markdown
## 작업 지시서

역할: ARCHITECT
작업: SQLAlchemy 모델 작성 및 Alembic 마이그레이션

수행 내용:
1. Alembic 초기화
   ```bash
   alembic init alembic
   ```

2. alembic/env.py 수정
   ```python
   from src.database import Base
   from src.users.models import User
   from src.checkin.models import CheckInLog
   from src.contacts.models import EmergencyContact
   from src.messages.models import PersonalMessage
   from src.notifications.models import NotificationLog
   
   target_metadata = Base.metadata
   ```

3. SPEC.md의 SQLAlchemy 모델을 각 모듈에 적용
   - src/users/models.py
   - src/checkin/models.py
   - src/contacts/models.py
   - src/messages/models.py
   - src/notifications/models.py

4. 초기 마이그레이션 생성
   ```bash
   alembic revision --autogenerate -m "init"
   alembic upgrade head
   ```

산출물:
- 각 모듈의 models.py (완성)
- alembic/versions/ (마이그레이션 파일)

완료 보고 형식으로 결과 제출
```

---

#### ⚙️ BACKEND DEV 작업

**Task 1-2: Auth 모듈 구현**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 인증/인가 모듈 구현 (FastAPI)

의존성: Task 1-1 (DB 스키마) 완료 필요

수행 내용:
1. Auth 모듈 구현 (src/auth/)
   - router.py: API 엔드포인트
   - service.py: 비즈니스 로직
   - schemas.py: Pydantic 스키마
   - dependencies.py: 현재 사용자 의존성

2. API 엔드포인트
   - POST /api/v1/auth/register
   - POST /api/v1/auth/login
   - POST /api/v1/auth/refresh
   - POST /api/v1/auth/forgot-password

3. JWT 구현 (src/common/security.py)
   - Access Token (15분)
   - Refresh Token (7일)
   - python-jose 사용

4. 비밀번호 해싱 (passlib + bcrypt)

5. 의존성 구현
   ```python
   # src/auth/dependencies.py
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2PasswordBearer
   from jose import JWTError, jwt
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
   
   async def get_current_user(
       token: str = Depends(oauth2_scheme),
       db: Session = Depends(get_db)
   ) -> User:
       # JWT 검증 및 사용자 반환
       pass
   ```

참조: SPEC.md > 3.1 인증 API

산출물:
- src/auth/* (완성된 모듈)
- 단위 테스트 (tests/test_auth.py)

완료 보고 형식으로 결과 제출
```

**Task 1-3: User 모듈 구현**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 사용자 모듈 구현

의존성: Task 1-2 (Auth 모듈) 완료 필요

수행 내용:
1. User 모듈 구현 (src/users/)
   - router.py
   - service.py
   - schemas.py

2. API 엔드포인트
   - GET /api/v1/users/me
   - PUT /api/v1/users/me
   - PUT /api/v1/users/me/fcm-token
   - DELETE /api/v1/users/me

3. CheckIn 설정 API (src/checkin/)
   - PUT /api/v1/checkin/settings
   - GET /api/v1/checkin/status

참조: SPEC.md > 3.5 사용자 API, 3.2 체크인 API

산출물:
- src/users/* (완성된 모듈)
- src/checkin/* (설정 부분만)

완료 보고 형식으로 결과 제출
```

---

#### 📱 FRONTEND DEV 작업

**Task 1-4: 인증 화면 구현**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: 로그인/회원가입 화면 구현

의존성: Task 1-2 (Auth API) 완료 필요

수행 내용:
1. 인증 화면 구현
   - app/(auth)/login.tsx
   - app/(auth)/register.tsx
   - app/(auth)/forgot-password.tsx

2. 인증 서비스 구현
   - services/auth.service.ts
   - API 호출 함수

3. 인증 상태 관리
   - stores/auth.store.ts (Zustand)
   - 토큰 저장 (AsyncStorage)
   - 자동 로그인

4. API 인스턴스 설정
   - services/api.ts
   - Axios interceptor (토큰 자동 첨부, 갱신)

5. 폼 유효성 검사
   - react-hook-form + zod

UI 요구사항:
- 깔끔하고 신뢰감 있는 디자인
- 로딩 상태 표시
- 에러 메시지 표시

산출물:
- 완성된 인증 화면
- 스크린샷 첨부

완료 보고 형식으로 결과 제출
```

**Task 1-5: 홈 화면 구현**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: 메인 홈 화면 (체크인 화면) 구현

의존성: Task 1-3 (User/CheckIn API), Task 1-4 (인증 화면)

수행 내용:
1. 탭 네비게이션 구성
   - app/(tabs)/_layout.tsx
   - 홈, 연락처, 메시지, 설정 탭

2. 홈 화면 구현
   - app/(tabs)/home.tsx
   - 체크인 상태 표시 (남은 일수)
   - "괜찮아요" 체크인 버튼
   - 마지막 체크인 시간

3. 설정 화면 (기본)
   - app/(tabs)/settings.tsx
   - 체크인 주기 변경
   - 로그아웃

4. 체크인 서비스
   - services/checkin.service.ts

UI 요구사항:
- 남은 일수 큰 숫자로 표시
- 체크인 버튼 눈에 띄게
- 따뜻하고 안심되는 색상

산출물:
- 완성된 홈/설정 화면
- 스크린샷 첨부

완료 보고 형식으로 결과 제출
```

---

## ⚡ PHASE 2: 핵심 로직

### 목표
- 체크인 기록 저장
- 비상연락처 관리
- 미체크 감지 및 알림 발송

### 에이전트별 작업

---

#### 🎯 ORCHESTRATOR 지시

```markdown
## Phase 2 시작

목표: 핵심 비즈니스 로직 구현

의존성 그래프:
```
BACKEND DEV (CheckIn 기록)
       │
       ├──▶ BACKEND DEV (Contacts API) ──▶ FRONTEND DEV (Contacts UI)
       │
       ├──▶ BACKEND DEV (Messages API) ──▶ FRONTEND DEV (Messages UI)
       │
       └──▶ SCHEDULER (Celery 배치) ──▶ SCHEDULER (알림 발송)
```

작업 순서:
1. BACKEND DEV → CheckIn 기록 API 완성
2. BACKEND DEV → Contacts, Messages API
3. FRONTEND DEV → Contacts, Messages 화면
4. SCHEDULER → 미체크 감지 배치 (Celery)
5. SCHEDULER → FCM, 이메일 발송

완료 조건:
- [ ] 체크인 수행 시 기록 저장
- [ ] 비상연락처 CRUD 작동
- [ ] 개인 메시지 저장/조회 작동
- [ ] Celery 배치 실행 시 미체크 대상자 감지
- [ ] 테스트 알림 발송 성공
```

---

#### ⚙️ BACKEND DEV 작업

**Task 2-1: CheckIn 기록 API**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 체크인 기록 저장 API 완성

수행 내용:
1. CheckIn 모듈 완성 (src/checkin/)
   - POST /api/v1/checkin (체크인 수행)
   - GET /api/v1/checkin/history (기록 조회)

2. 체크인 로직
   - check_in_logs 테이블에 기록
   - users.last_check_in 업데이트
   - 다음 체크인 기한 계산

참조: SPEC.md > 3.2 체크인 API, 4.1 체크인 시스템

산출물:
- src/checkin/* (완성)
- 단위 테스트 (tests/test_checkin.py)

완료 보고 형식으로 결과 제출
```

**Task 2-2: Contacts API**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 비상연락처 CRUD API 구현

수행 내용:
1. Contacts 모듈 구현 (src/contacts/)
   - GET /api/v1/contacts
   - POST /api/v1/contacts
   - PUT /api/v1/contacts/{contact_id}
   - DELETE /api/v1/contacts/{contact_id}
   - POST /api/v1/contacts/{contact_id}/verify

2. 비즈니스 규칙
   - 최대 3명 제한
   - 중복 연락처 방지
   - priority 자동 관리

참조: SPEC.md > 3.3 비상연락처 API

산출물:
- src/contacts/* (완성)
- 단위 테스트

완료 보고 형식으로 결과 제출
```

**Task 2-3: Messages API**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 개인 메시지 API 구현

수행 내용:
1. Messages 모듈 구현 (src/messages/)
   - GET /api/v1/message
   - PUT /api/v1/message
   - DELETE /api/v1/message

2. 보안 요구사항
   - 내용 암호화 저장 (AES-256)
   - 글자 수 제한 (2000자)
   
3. 암호화 유틸리티 (src/common/encryption.py)
   ```python
   from cryptography.fernet import Fernet
   
   def encrypt_message(content: str, key: bytes) -> str:
       f = Fernet(key)
       return f.encrypt(content.encode()).decode()
   
   def decrypt_message(encrypted: str, key: bytes) -> str:
       f = Fernet(key)
       return f.decrypt(encrypted.encode()).decode()
   ```

참조: SPEC.md > 3.4 개인 메시지 API

산출물:
- src/messages/* (완성)
- src/common/encryption.py
- 단위 테스트

완료 보고 형식으로 결과 제출
```

---

#### 📱 FRONTEND DEV 작업

**Task 2-4: Contacts 화면**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: 비상연락처 관리 화면 구현

의존성: Task 2-2 (Contacts API)

수행 내용:
1. 연락처 화면 구현
   - app/(tabs)/contacts.tsx
   - 연락처 목록
   - 추가/수정/삭제

2. 연락처 추가 모달
   - 이름, 연락 수단 선택, 연락처 입력
   - 폼 유효성 검사

3. 서비스 연동
   - services/contacts.service.ts

UI 요구사항:
- 연락처별 인증 상태 표시
- 삭제 확인 모달
- 최대 3명 제한 안내

산출물:
- 완성된 연락처 화면
- 스크린샷 첨부

완료 보고 형식으로 결과 제출
```

**Task 2-5: Message 화면**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: 개인 메시지 작성 화면 구현

의존성: Task 2-3 (Messages API)

수행 내용:
1. 메시지 화면 구현
   - app/(tabs)/message.tsx
   - 텍스트 입력 영역
   - 글자 수 카운터
   - 저장/삭제 버튼

2. 발송 여부 토글
   - 메시지 활성화/비활성화

3. 서비스 연동
   - services/message.service.ts

UI 요구사항:
- 충분한 입력 공간
- 자동 저장 또는 저장 버튼
- 안내 문구 표시

산출물:
- 완성된 메시지 화면
- 스크린샷 첨부

완료 보고 형식으로 결과 제출
```

---

#### ⏰ SCHEDULER 작업

**Task 2-6: Celery 미체크 감지 배치**

```markdown
## 작업 지시서

역할: SCHEDULER
작업: Celery 기반 미체크 감지 배치 작업 구현

수행 내용:
1. Celery 설정 (src/scheduler/celery_app.py)
   ```python
   from celery import Celery
   from celery.schedules import crontab
   from src.config import settings

   celery_app = Celery(
       "solocheck",
       broker=settings.REDIS_URL,
       backend=settings.REDIS_URL
   )

   celery_app.conf.beat_schedule = {
       "check-missed-checkins-midnight": {
           "task": "src.scheduler.tasks.check_missed_checkins",
           "schedule": crontab(hour=0, minute=0),
       },
       "check-missed-checkins-noon": {
           "task": "src.scheduler.tasks.check_missed_checkins",
           "schedule": crontab(hour=12, minute=0),
       },
   }
   ```

2. 배치 태스크 구현 (src/scheduler/tasks.py)
   - check_missed_checkins: 미체크 대상자 감지
   - send_alert_to_contacts: 알림 발송
   - send_reminder_notifications: 리마인더 발송

3. Docker Compose에 Celery 추가
   ```yaml
   celery-worker:
     build: .
     command: celery -A src.scheduler.celery_app worker --loglevel=info
     depends_on:
       - redis
       - db

   celery-beat:
     build: .
     command: celery -A src.scheduler.celery_app beat --loglevel=info
     depends_on:
       - redis
   ```

참조: SPEC.md > 4.2 미체크 감지 시스템

산출물:
- src/scheduler/* (완성)
- docker-compose.yml (Celery 추가)
- 배치 테스트 로그

완료 보고 형식으로 결과 제출
```

**Task 2-7: 알림 발송 시스템**

```markdown
## 작업 지시서

역할: SCHEDULER
작업: FCM 푸시 및 이메일 발송 구현

수행 내용:
1. Notifications 모듈 구현 (src/notifications/)
   - service.py: FCM, SendGrid 발송
   - templates.py: 알림 템플릿

2. FCM 발송 (firebase-admin)
   ```python
   import firebase_admin
   from firebase_admin import credentials, messaging

   def send_push_notification(token: str, title: str, body: str):
       message = messaging.Message(
           notification=messaging.Notification(title=title, body=body),
           token=token
       )
       return messaging.send(message)
   ```

3. 이메일 발송 (SendGrid)
   ```python
   from sendgrid import SendGridAPIClient
   from sendgrid.helpers.mail import Mail

   def send_email(to_email: str, subject: str, content: str):
       message = Mail(
           from_email="noreply@solocheck.app",
           to_emails=to_email,
           subject=subject,
           html_content=content
       )
       sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
       return sg.send(message)
   ```

4. 알림 템플릿 (SPEC.md 참조)
   - 상태 알림 템플릿
   - 개인 메시지 포함 템플릿

5. 발송 로그 기록
   - notification_logs 테이블

참조: SPEC.md > 4.3 알림 템플릿, 4.4 푸시 알림

산출물:
- src/notifications/* (완성)
- 발송 테스트 결과

완료 보고 형식으로 결과 제출
```

---

## 🛡️ PHASE 3: 안정화

### 목표
- 예외 처리 강화
- 법적 고지 페이지
- 테스트 커버리지 확보

---

#### 🎯 ORCHESTRATOR 지시

```markdown
## Phase 3 시작

목표: 서비스 안정화 및 법적 요구사항 충족

작업 순서:
1. BACKEND DEV → 예외 처리, 로깅 강화
2. FRONTEND DEV → 에러 화면, 고지 페이지
3. QA → 전체 테스트 케이스 작성 및 실행

완료 조건:
- [ ] 모든 API 에러 응답 일관성
- [ ] 앱 크래시 없음
- [ ] 필수 고지 문구 표시
- [ ] 테스트 커버리지 70% 이상
```

---

#### ⚙️ BACKEND DEV 작업

**Task 3-1: 예외 처리 강화**

```markdown
## 작업 지시서

역할: BACKEND DEV
작업: 글로벌 예외 처리 및 로깅

수행 내용:
1. 커스텀 예외 클래스 (src/common/exceptions.py)
   ```python
   from fastapi import HTTPException

   class SoloCheckException(HTTPException):
       def __init__(self, code: str, message: str, status_code: int = 400):
           self.code = code
           super().__init__(status_code=status_code, detail={"code": code, "message": message})
   
   class AuthException(SoloCheckException):
       pass
   
   class CheckInException(SoloCheckException):
       pass
   ```

2. 글로벌 예외 핸들러 (src/main.py)
   ```python
   from fastapi import Request
   from fastapi.responses import JSONResponse

   @app.exception_handler(SoloCheckException)
   async def solocheck_exception_handler(request: Request, exc: SoloCheckException):
       return JSONResponse(
           status_code=exc.status_code,
           content={"code": exc.code, "message": exc.detail["message"]}
       )
   ```

3. 로깅 설정
   - Python logging 모듈
   - 민감 정보 마스킹

4. Rate Limiting (slowapi)
   ```bash
   pip install slowapi
   ```

산출물:
- src/common/exceptions.py
- 로깅 설정
- Rate limiting 적용

완료 보고 형식으로 결과 제출
```

---

#### 📱 FRONTEND DEV 작업

**Task 3-2: 에러 처리 및 고지 페이지**

```markdown
## 작업 지시서

역할: FRONTEND DEV
작업: 에러 화면 및 법적 고지 페이지

수행 내용:
1. 에러 처리
   - API 에러 토스트/모달
   - 네트워크 에러 화면
   - 세션 만료 처리

2. 법적 고지 페이지
   - 서비스 이용약관
   - 개인정보 처리방침
   - 서비스 설명 (필수 고지 문구 포함)

3. 온보딩 화면
   - 첫 사용자 가이드
   - 서비스 목적 설명

참조: CLAUDE.md > 7. 필수 고지 문구

산출물:
- 에러 처리 구현
- 고지 페이지
- 온보딩 화면

완료 보고 형식으로 결과 제출
```

---

#### 🧪 QA 작업

**Task 3-3: 테스트 케이스 작성**

```markdown
## 작업 지시서

역할: QA
작업: 테스트 케이스 작성 및 실행

수행 내용:
1. 단위 테스트 (Backend - pytest)
   - tests/test_auth.py
   - tests/test_checkin.py
   - tests/test_contacts.py
   - tests/test_messages.py

2. 통합 테스트
   - API E2E 테스트 (httpx)
   - 알림 발송 플로우

3. 주요 시나리오
   - 회원가입 → 설정 → 체크인 플로우
   - 연락처 등록 플로우
   - 미체크 → 알림 발송 플로우

4. 엣지 케이스
   - 동시 체크인
   - 연락처 3명 초과 시도
   - 잘못된 토큰
   - 만료된 토큰

산출물:
- tests/ (테스트 코드)
- 테스트 결과 리포트
- 발견된 버그 목록

완료 보고 형식으로 결과 제출
```

---

## 🚢 PHASE 4: 릴리즈 준비

### 목표
- 최종 점검
- 문서화
- 빌드 및 배포 준비

---

#### 🎯 ORCHESTRATOR 지시

```markdown
## Phase 4 시작 (최종)

목표: MVP 릴리즈 준비

작업 순서:
1. QA → 최종 테스트 및 버그 수정
2. BACKEND DEV → API 문서화 (Swagger/OpenAPI)
3. FRONTEND DEV → 앱 빌드 설정
4. ORCHESTRATOR → 최종 검토

완료 조건:
- [ ] 모든 Critical 버그 수정
- [ ] API 문서 완성 (FastAPI 자동 문서: /docs)
- [ ] iOS/Android 빌드 성공
- [ ] README 최종 업데이트

MVP 성공 기준 (CLAUDE.md 참조):
- [ ] 체크인 성공률 추적 가능
- [ ] 미체크 → 알림 정상 발송
- [ ] 사용자 1명이 전체 플로우 완료 가능
- [ ] 법적 리스크 없이 서비스 설명 가능
```

---

## 📌 작업 추적 템플릿

### 작업 상태 표
```markdown
| Phase | Task ID | 담당 | 작업 | 상태 | 비고 |
|-------|---------|------|------|------|------|
| 0 | 0-1 | BACKEND | FastAPI 프로젝트 초기화 | ⬜ 대기 | |
| 0 | 0-2 | FRONTEND | Expo 프로젝트 초기화 | ⬜ 대기 | |
| 1 | 1-1 | ARCHITECT | SQLAlchemy 모델 & Alembic | ⬜ 대기 | |
| 1 | 1-2 | BACKEND | Auth 모듈 | ⬜ 대기 | 1-1 의존 |
| 1 | 1-3 | BACKEND | User 모듈 | ⬜ 대기 | 1-2 의존 |
| 1 | 1-4 | FRONTEND | 인증 화면 | ⬜ 대기 | 1-2 의존 |
| 1 | 1-5 | FRONTEND | 홈 화면 | ⬜ 대기 | 1-3, 1-4 의존 |
| 2 | 2-1 | BACKEND | CheckIn 기록 API | ⬜ 대기 | |
| 2 | 2-2 | BACKEND | Contacts API | ⬜ 대기 | |
| 2 | 2-3 | BACKEND | Messages API | ⬜ 대기 | |
| 2 | 2-4 | FRONTEND | Contacts 화면 | ⬜ 대기 | 2-2 의존 |
| 2 | 2-5 | FRONTEND | Message 화면 | ⬜ 대기 | 2-3 의존 |
| 2 | 2-6 | SCHEDULER | Celery 배치 | ⬜ 대기 | |
| 2 | 2-7 | SCHEDULER | 알림 발송 | ⬜ 대기 | 2-6 의존 |
| 3 | 3-1 | BACKEND | 예외 처리 | ⬜ 대기 | |
| 3 | 3-2 | FRONTEND | 에러/고지 페이지 | ⬜ 대기 | |
| 3 | 3-3 | QA | 테스트 케이스 | ⬜ 대기 | |
| 4 | 4-1 | ALL | 최종 검토 | ⬜ 대기 | |

상태: ⬜ 대기 / 🔄 진행중 / ✅ 완료 / ❌ 블로킹
```

---

## 🔄 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-19 | 최초 작성 |
| 1.1 | 2025-01-19 | Python 스택으로 변경 (FastAPI, SQLAlchemy, Celery) |

---

> **이 문서는 실행 계획입니다. 작업 순서와 의존성을 반드시 준수하세요.**
