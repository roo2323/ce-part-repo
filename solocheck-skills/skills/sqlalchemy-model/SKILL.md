---
name: sqlalchemy-model
description: SQLAlchemy ORM 모델 설계 시 사용. ARCHITECT 전용. 모델 클래스 작성 가이드.
---

# SQLAlchemy 모델 설계 체크리스트

## 클래스 구조
- [ ] `Base` 클래스 상속
- [ ] `__tablename__` 명시 (snake_case, 복수형)
- [ ] 클래스명 PascalCase, 단수형

## Primary Key
- [ ] UUID 사용 (`String(36)`)
- [ ] `default=lambda: str(uuid.uuid4())`
- [ ] `primary_key=True`

## 컬럼 정의
- [ ] 타입 명시 (`String`, `Integer`, `Boolean`, `DateTime`)
- [ ] `nullable` 명시 (기본 True, 필수 필드는 False)
- [ ] `unique` 필요 시 명시
- [ ] `index=True` 필요 시 명시
- [ ] `default` 값 설정

## 타임스탬프
- [ ] `DateTime(timezone=True)` 사용
- [ ] `server_default=func.now()` 설정
- [ ] `updated_at`에 `onupdate=func.now()` 설정

## Relationship
- [ ] `relationship()` 양방향 설정
- [ ] `back_populates` 사용
- [ ] `cascade="all, delete-orphan"` 설정 (부모-자식)
- [ ] `uselist=False` (1:1 관계)

---

## 모델 템플릿
```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
```

---

## 완료 확인
- [ ] ERD와 일치
- [ ] 모든 필드 정의 완료
- [ ] 관계 설정 완료
- [ ] BACKEND_DEV 인계 준비
