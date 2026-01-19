# SPEC.md - SoloCheck 요구사항 설계도

> 이 문서는 프로젝트의 기능 요구사항, 데이터 모델, API 명세를 정의합니다.

---

## 1. 시스템 아키텍처

### 1.1 전체 구조
```
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                              │
│                   (React Native + Expo)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Auth    │  │ CheckIn  │  │ Contacts │  │ Message  │        │
│  │  Screen  │  │  Screen  │  │  Screen  │  │  Screen  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       └─────────────┴─────────────┴─────────────┘              │
│                          │                                      │
│                    Expo Push Token                              │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVER                              │
│                        (FastAPI)                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │ Auth       │  │ CheckIn    │  │ Contacts   │                 │
│  │ Router     │  │ Router     │  │ Router     │                 │
│  └────────────┘  └────────────┘  └────────────┘                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │ Message    │  │ Scheduler  │  │ Notify     │                 │
│  │ Router     │  │ (Celery)   │  │ Service    │                 │
│  └────────────┘  └────────────┘  └────────────┘                 │
│         │              │               │                         │
└─────────┼──────────────┼───────────────┼─────────────────────────┘
          │              │               │
          ▼              ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ PostgreSQL │  │   Redis    │  │    FCM     │
   │  (Data)    │  │  (Celery)  │  │  (Push)    │
   └────────────┘  └────────────┘  └────────────┘
                                         │
                                         ▼
                                  ┌────────────┐
                                  │  SendGrid  │
                                  │  (Email)   │
                                  └────────────┘
```

### 1.2 레포지토리 구조

#### solocheck-app (React Native)
```
solocheck-app/
├── app/                    # Expo Router 페이지
│   ├── (auth)/            # 인증 관련 화면
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   └── forgot-password.tsx
│   ├── (tabs)/            # 메인 탭 화면
│   │   ├── home.tsx       # 체크인 메인
│   │   ├── contacts.tsx   # 비상연락처
│   │   ├── message.tsx    # 개인 메시지
│   │   └── settings.tsx   # 설정
│   ├── _layout.tsx
│   └── index.tsx
├── components/            # 재사용 컴포넌트
│   ├── ui/               # 기본 UI 컴포넌트
│   ├── check-in/         # 체크인 관련
│   └── contacts/         # 연락처 관련
├── hooks/                # 커스텀 훅
├── services/             # API 서비스
│   ├── api.ts           # Axios 인스턴스
│   ├── auth.service.ts
│   ├── checkin.service.ts
│   └── contacts.service.ts
├── stores/               # 상태 관리 (Zustand)
├── utils/                # 유틸리티
├── constants/            # 상수
├── types/                # TypeScript 타입
├── app.json
├── package.json
└── tsconfig.json
```

#### solocheck-backend (FastAPI + Python)
```
solocheck-backend/
├── src/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 (환경변수)
│   ├── database.py             # DB 연결 설정
│   │
│   ├── auth/                   # 인증 모듈
│   │   ├── __init__.py
│   │   ├── router.py          # API 라우터
│   │   ├── service.py         # 비즈니스 로직
│   │   ├── schemas.py         # Pydantic 스키마
│   │   └── dependencies.py    # 의존성 (현재 사용자 등)
│   │
│   ├── users/                  # 사용자 모듈
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py          # SQLAlchemy 모델
│   │
│   ├── checkin/                # 체크인 모듈
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py
│   │
│   ├── contacts/               # 비상연락처 모듈
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py
│   │
│   ├── messages/               # 개인 메시지 모듈
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py
│   │
│   ├── notifications/          # 알림 모듈
│   │   ├── __init__.py
│   │   ├── service.py         # FCM, 이메일 발송
│   │   ├── templates.py       # 알림 템플릿
│   │   └── models.py
│   │
│   ├── scheduler/              # Celery 태스크
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery 설정
│   │   └── tasks.py           # 배치 태스크
│   │
│   └── common/                 # 공통 유틸
│       ├── __init__.py
│       ├── exceptions.py      # 커스텀 예외
│       ├── security.py        # JWT, 암호화
│       └── utils.py
│
├── alembic/                    # DB 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── tests/                      # 테스트
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_checkin.py
│   └── ...
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 2. 데이터베이스 스키마

### 2.1 ERD
```
┌───────────────────┐       ┌───────────────────┐
│      users        │       │   check_in_logs   │
├───────────────────┤       ├───────────────────┤
│ id (PK)           │──┐    │ id (PK)           │
│ email             │  │    │ user_id (FK)      │──┐
│ password_hash     │  │    │ checked_at        │  │
│ nickname          │  │    │ method            │  │
│ check_in_cycle    │  │    │ created_at        │  │
│ grace_period      │  │    └───────────────────┘  │
│ last_check_in     │  │                           │
│ fcm_token         │  │    ┌───────────────────┐  │
│ is_active         │  │    │emergency_contacts │  │
│ created_at        │  │    ├───────────────────┤  │
│ updated_at        │  └───▶│ id (PK)           │  │
└───────────────────┘       │ user_id (FK)      │◀─┘
         │                  │ name              │
         │                  │ contact_type      │
         │                  │ contact_value     │
         │                  │ priority          │
         │                  │ is_verified       │
         │                  │ created_at        │
         │                  └───────────────────┘
         │
         │                  ┌───────────────────┐
         │                  │  personal_messages│
         │                  ├───────────────────┤
         └─────────────────▶│ id (PK)           │
                            │ user_id (FK)      │
                            │ content           │
                            │ is_enabled        │
                            │ created_at        │
                            │ updated_at        │
                            └───────────────────┘

┌───────────────────┐
│ notification_logs │
├───────────────────┤
│ id (PK)           │
│ user_id (FK)      │
│ contact_id (FK)   │
│ type              │
│ status            │
│ sent_at           │
│ error_message     │
└───────────────────┘
```

### 2.2 SQLAlchemy Models

```python
# src/users/models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    
    # 체크인 설정
    check_in_cycle = Column(Integer, default=7)  # 일 단위
    grace_period = Column(Integer, default=48)   # 시간 단위
    last_check_in = Column(DateTime(timezone=True), nullable=True)
    
    # 푸시 토큰
    fcm_token = Column(String(500), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    check_in_logs = relationship("CheckInLog", back_populates="user", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    personal_message = relationship("PersonalMessage", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notification_logs = relationship("NotificationLog", back_populates="user", cascade="all, delete-orphan")
```

```python
# src/checkin/models.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class CheckInLog(Base):
    __tablename__ = "check_in_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    method = Column(String(50))  # 'app_open' | 'button_click' | 'push_response'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="check_in_logs")
```

```python
# src/contacts/models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    contact_type = Column(String(20), nullable=False)  # 'email' | 'sms'
    contact_value = Column(String(255), nullable=False)
    priority = Column(Integer, default=1)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="emergency_contacts")
    notification_logs = relationship("NotificationLog", back_populates="contact", cascade="all, delete-orphan")
```

```python
# src/messages/models.py

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class PersonalMessage(Base):
    __tablename__ = "personal_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    content = Column(Text, nullable=False)  # 암호화 저장
    is_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personal_message")
```

```python
# src/notifications/models.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(String(36), ForeignKey("emergency_contacts.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50))  # 'status_alert' | 'personal_message'
    status = Column(String(20))  # 'pending' | 'sent' | 'failed'
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_logs")
    contact = relationship("EmergencyContact", back_populates="notification_logs")
```

### 2.3 Database Connection

```python
# src/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3. API 명세

### 3.1 인증 API

#### POST /api/v1/auth/register
회원가입
```python
# Request
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "홍길동"  # optional
}

# Response 201
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "홍길동",
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/login
로그인
```python
# Request
{
  "email": "user@example.com",
  "password": "password123"
}

# Response 200
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "nickname": "홍길동"
  }
}
```

#### POST /api/v1/auth/refresh
토큰 갱신
```python
# Request
{
  "refresh_token": "refresh_token"
}

# Response 200
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/forgot-password
비밀번호 재설정 요청
```python
# Request
{
  "email": "user@example.com"
}

# Response 200
{
  "message": "비밀번호 재설정 이메일이 발송되었습니다."
}
```

---

### 3.2 체크인 API

#### POST /api/v1/checkin
체크인 수행
```python
# Request
{
  "method": "button_click"  # 'app_open' | 'button_click' | 'push_response'
}

# Response 201
{
  "id": "uuid",
  "checked_at": "2025-01-19T12:00:00Z",
  "next_check_in_due": "2025-01-26T12:00:00Z",
  "message": "체크인 완료! 다음 체크인까지 7일 남았습니다."
}
```

#### GET /api/v1/checkin/status
체크인 상태 조회
```python
# Response 200
{
  "last_check_in": "2025-01-19T12:00:00Z",
  "next_check_in_due": "2025-01-26T12:00:00Z",
  "days_remaining": 7,
  "hours_remaining": 168,
  "is_overdue": false,
  "check_in_cycle": 7,
  "grace_period": 48
}
```

#### PUT /api/v1/checkin/settings
체크인 설정 변경
```python
# Request
{
  "check_in_cycle": 14,   # 7 | 14 | 30
  "grace_period": 48      # 24 | 48 | 72
}

# Response 200
{
  "check_in_cycle": 14,
  "grace_period": 48,
  "next_check_in_due": "2025-02-02T12:00:00Z"
}
```

#### GET /api/v1/checkin/history
체크인 기록 조회
```python
# Query: ?page=1&limit=20

# Response 200
{
  "data": [
    {
      "id": "uuid",
      "checked_at": "2025-01-19T12:00:00Z",
      "method": "button_click"
    }
  ],
  "meta": {
    "total": 50,
    "page": 1,
    "limit": 20,
    "total_pages": 3
  }
}
```

---

### 3.3 비상연락처 API

#### GET /api/v1/contacts
비상연락처 목록 조회
```python
# Response 200
{
  "data": [
    {
      "id": "uuid",
      "name": "김철수",
      "contact_type": "email",
      "contact_value": "kim@example.com",
      "priority": 1,
      "is_verified": true
    }
  ],
  "max_contacts": 3,
  "current_count": 1
}
```

#### POST /api/v1/contacts
비상연락처 등록
```python
# Request
{
  "name": "김철수",
  "contact_type": "email",
  "contact_value": "kim@example.com",
  "priority": 1
}

# Response 201
{
  "id": "uuid",
  "name": "김철수",
  "contact_type": "email",
  "contact_value": "kim@example.com",
  "priority": 1,
  "is_verified": false
}
```

#### PUT /api/v1/contacts/{contact_id}
비상연락처 수정
```python
# Request
{
  "name": "김철수 (형)",
  "priority": 2
}

# Response 200
{
  "id": "uuid",
  "name": "김철수 (형)",
  "contact_type": "email",
  "contact_value": "kim@example.com",
  "priority": 2,
  "is_verified": true
}
```

#### DELETE /api/v1/contacts/{contact_id}
비상연락처 삭제
```python
# Response 204 No Content
```

#### POST /api/v1/contacts/{contact_id}/verify
연락처 확인 재발송
```python
# Response 200
{
  "message": "확인 메일이 발송되었습니다."
}
```

---

### 3.4 개인 메시지 API

#### GET /api/v1/message
개인 메시지 조회
```python
# Response 200
{
  "id": "uuid",
  "content": "안녕하세요, 이 메시지를 보신다면...",
  "is_enabled": true,
  "character_count": 150,
  "max_characters": 2000,
  "updated_at": "2025-01-19T12:00:00Z"
}

# Response 404 (메시지 없음)
{
  "content": null,
  "is_enabled": false
}
```

#### PUT /api/v1/message
개인 메시지 저장/수정
```python
# Request
{
  "content": "안녕하세요, 이 메시지를 보신다면...",
  "is_enabled": true
}

# Response 200
{
  "id": "uuid",
  "content": "안녕하세요, 이 메시지를 보신다면...",
  "is_enabled": true,
  "character_count": 150,
  "updated_at": "2025-01-19T12:00:00Z"
}
```

#### DELETE /api/v1/message
개인 메시지 삭제
```python
# Response 204 No Content
```

---

### 3.5 사용자 API

#### GET /api/v1/users/me
내 정보 조회
```python
# Response 200
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "홍길동",
  "check_in_cycle": 7,
  "grace_period": 48,
  "last_check_in": "2025-01-19T12:00:00Z",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### PUT /api/v1/users/me
내 정보 수정
```python
# Request
{
  "nickname": "새닉네임"
}

# Response 200
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "새닉네임",
  ...
}
```

#### PUT /api/v1/users/me/fcm-token
FCM 토큰 업데이트
```python
# Request
{
  "fcm_token": "expo_push_token_or_fcm_token"
}

# Response 200
{
  "message": "토큰이 업데이트되었습니다."
}
```

#### DELETE /api/v1/users/me
회원 탈퇴
```python
# Request
{
  "password": "current_password"
}

# Response 204 No Content
```

---

## 4. 기능 상세 명세

### 4.1 체크인 시스템

#### 체크인 주기 옵션
| 주기 | 유예 기간 | 총 기간 |
|------|----------|---------|
| 7일 | 48시간 | 9일 |
| 14일 | 48시간 | 16일 |
| 30일 | 48시간 | 32일 |

#### 체크인 방식
1. **앱 접속 자동 체크인**: 앱 포그라운드 진입 시
2. **버튼 클릭**: "괜찮아요" 버튼 명시적 클릭
3. **푸시 응답**: 리마인더 푸시 알림에서 직접 응답

#### 체크인 플로우
```
앱 접속
    │
    ▼
┌─────────────┐
│ 마지막 체크인 │
│ 확인        │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  기한 내?                            │
│  Yes ──▶ "다음 체크인까지 N일"        │
│  No  ──▶ "체크인이 필요합니다" + 버튼  │
└─────────────────────────────────────┘
       │
       ▼
    체크인 수행
       │
       ▼
┌─────────────┐
│ check_in_logs│
│ 기록 저장    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ users.      │
│ last_check_in│
│ 업데이트     │
└─────────────┘
```

---

### 4.2 미체크 감지 시스템 (Celery)

#### Celery 설정
```python
# src/scheduler/celery_app.py

from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    "solocheck",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# 배치 스케줄 (매일 00:00, 12:00 UTC)
celery_app.conf.beat_schedule = {
    "check-missed-checkins-midnight": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=0, minute=0),
    },
    "check-missed-checkins-noon": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=12, minute=0),
    },
    "send-reminder-notifications": {
        "task": "src.scheduler.tasks.send_reminder_notifications",
        "schedule": crontab(hour="*/6"),  # 6시간마다
    },
}
```

#### 감지 로직
```python
# src/scheduler/tasks.py

from celery import shared_task
from sqlalchemy import text
from datetime import datetime, timezone
from src.database import SessionLocal


@shared_task
def check_missed_checkins():
    """미체크 대상자 감지 및 알림 발송"""
    db = SessionLocal()
    try:
        # 미체크 대상자 조회
        query = text("""
            SELECT * FROM users
            WHERE is_active = true
              AND last_check_in IS NOT NULL
              AND last_check_in + INTERVAL '1 day' * check_in_cycle 
                  + INTERVAL '1 hour' * grace_period < NOW()
        """)
        
        missed_users = db.execute(query).fetchall()
        
        for user in missed_users:
            # 알림 발송 태스크 큐에 등록
            send_alert_to_contacts.delay(user.id)
            
    finally:
        db.close()


@shared_task
def send_alert_to_contacts(user_id: str):
    """비상연락처에 알림 발송"""
    # FCM, 이메일 발송 로직
    pass


@shared_task
def send_reminder_notifications():
    """체크인 리마인더 발송"""
    # 24시간 전 알림 대상자 조회 및 푸시 발송
    pass
```

#### 알림 발송 플로우
```
배치 작업 시작 (Celery Beat)
       │
       ▼
┌─────────────────┐
│ 미체크 대상자    │
│ 조회            │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ 대상 있음? │
    └────┬────┘
    Yes  │  No ──▶ 종료
         │
         ▼
┌─────────────────┐
│ 각 대상자별      │
│ Celery Task 생성 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ priority 순서로  │
│ 알림 발송        │
└────────┬────────┘
         │
         ├──▶ 1단계: 상태 알림
         │
         └──▶ 2단계: 개인 메시지 (활성화 시)
         │
         ▼
┌─────────────────┐
│ notification_logs│
│ 기록            │
└─────────────────┘
```

---

### 4.3 알림 템플릿

#### 상태 알림 (이메일)
```
제목: [SoloCheck] {nickname}님의 안부 확인이 필요합니다

본문:
안녕하세요, {contact_name}님.

{nickname}님이 {days}일간 SoloCheck 앱에서 안부 확인을 하지 않았습니다.

이 알림은 {nickname}님이 미리 설정한 비상 연락망을 통해 발송되었습니다.
직접 연락을 시도해 주시기 바랍니다.

※ 본 서비스는 사망 여부를 확인하지 않습니다.
※ 긴급 상황 시 112/119 등 공공기관에 연락하세요.

---
SoloCheck
```

#### 개인 메시지 포함 (이메일)
```
제목: [SoloCheck] {nickname}님이 남긴 메시지가 있습니다

본문:
안녕하세요, {contact_name}님.

{nickname}님이 남긴 메시지를 전달드립니다.

---
{personal_message_content}
---

※ 위 메시지는 {nickname}님이 미리 작성해 둔 내용입니다.

---
SoloCheck
```

---

### 4.4 푸시 알림 (리마인더)

#### 체크인 리마인더
```
발송 시점: 체크인 기한 24시간 전

제목: 안부 확인 시간이에요 👋
내용: 체크인 기한이 24시간 남았어요. 앱에서 "괜찮아요"를 눌러주세요.
액션: 앱 열기, 체크인하기
```

#### 긴급 리마인더
```
발송 시점: 유예 기간 시작 시

제목: ⚠️ 체크인이 필요합니다
내용: 체크인 기한이 지났어요. 48시간 내에 체크인하지 않으면 비상연락처에 알림이 발송됩니다.
액션: 앱 열기, 체크인하기
```

---

## 5. 보안 요구사항

### 5.1 인증/인가
```python
# src/common/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Access Token: 15분, Refresh Token: 7일
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

### 5.2 데이터 보호
- 개인 메시지: AES-256 암호화 저장
- 민감 정보 로깅 금지
- HTTPS 필수

### 5.3 데이터 보관
- 체크인 로그: 1년 보관
- 비활성 계정: 1년 후 자동 정리 안내 → 30일 후 삭제
- 알림 로그: 6개월 보관

---

## 6. 기술 스택 요약

### 6.1 Backend (Python)
| 구분 | 기술 |
|------|------|
| Framework | FastAPI |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 15 |
| Task Queue | Celery + Redis |
| Auth | python-jose (JWT), passlib (bcrypt) |
| Email | SendGrid |
| Push | firebase-admin (FCM) |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio |

### 6.2 App (React Native)
| 구분 | 기술 |
|------|------|
| Framework | React Native + Expo |
| Language | TypeScript |
| State | Zustand |
| Push | Expo Notifications + FCM |
| Navigation | Expo Router |
| HTTP Client | Axios |
| Form | react-hook-form + zod |

### 6.3 Infrastructure
| 구분 | 기술 |
|------|------|
| Container | Docker + Docker Compose |
| Local Dev | PostgreSQL, Redis (Docker) |
| CI/CD | 추후 결정 |

---

## 7. 에러 코드

| 코드 | 메시지 | 설명 |
|------|--------|------|
| AUTH001 | 이메일 또는 비밀번호가 올바르지 않습니다 | 로그인 실패 |
| AUTH002 | 이미 가입된 이메일입니다 | 중복 가입 |
| AUTH003 | 토큰이 만료되었습니다 | JWT 만료 |
| CHECKIN001 | 이미 오늘 체크인했습니다 | 중복 체크인 |
| CONTACT001 | 비상연락처는 최대 3명까지 등록 가능합니다 | 초과 등록 |
| CONTACT002 | 이미 등록된 연락처입니다 | 중복 연락처 |
| MESSAGE001 | 메시지는 2000자를 초과할 수 없습니다 | 글자 수 초과 |

---

## 8. 버전 관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-19 | 최초 작성 |
| 1.1 | 2025-01-19 | Python 스택으로 변경 (FastAPI, SQLAlchemy, Celery) |

---

> **이 문서는 개발의 기준이 됩니다. 변경 시 ORCHESTRATOR의 승인이 필요합니다.**
