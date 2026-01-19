---
name: test-fixture
description: pytest Fixture 작성 시 사용. QA 전용. conftest.py 및 테스트 데이터 설정.
---

# 테스트 Fixture 체크리스트

## 파일 구조
- [ ] `tests/conftest.py` - 공통 Fixture
- [ ] 모듈별 conftest.py (필요 시)

## 필수 Fixture
- [ ] `setup_database` - DB 스키마 생성/삭제
- [ ] `db_session` - 트랜잭션 롤백 세션
- [ ] `client` - TestClient
- [ ] `test_user` - 기본 테스트 사용자
- [ ] `auth_headers` - 인증 헤더

## Fixture 범위 (scope)
- [ ] `session` - 전체 테스트 세션 (DB 스키마)
- [ ] `function` - 각 테스트 함수 (기본값)
- [ ] `class` - 각 테스트 클래스
- [ ] `module` - 각 테스트 모듈

## 테스트 격리
- [ ] 트랜잭션 롤백으로 데이터 격리
- [ ] 각 테스트 독립적 실행 보장

---

## conftest.py 전체 템플릿
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db
from src.users.models import User
from src.contacts.models import EmergencyContact
from src.common.security import get_password_hash, create_access_token

# ========== DB 설정 ==========
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ========== DB Fixture ==========
@pytest.fixture(scope="session")
def setup_database():
    """테스트 DB 스키마 생성 (세션 단위)"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """각 테스트별 DB 세션 (트랜잭션 롤백)"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# ========== Client Fixture ==========
@pytest.fixture
def client(db_session):
    """테스트 클라이언트"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ========== User Fixture ==========
@pytest.fixture
def test_user(db_session):
    """기본 테스트 사용자"""
    user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        nickname="테스트유저",
        check_in_cycle=7,
        grace_period=48,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """인증 헤더"""
    token = create_access_token({"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token():
    """만료된 토큰"""
    from datetime import datetime, timedelta
    from jose import jwt
    from src.config import settings
    
    payload = {
        "sub": "test-user-id",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


# ========== Domain Fixture ==========
@pytest.fixture
def one_contact(db_session, test_user):
    """연락처 1개"""
    contact = EmergencyContact(
        user_id=test_user.id,
        name="연락처1",
        contact_type="email",
        contact_value="contact1@example.com",
        priority=1
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact


@pytest.fixture
def three_contacts(db_session, test_user):
    """연락처 3개 (최대)"""
    contacts = []
    for i in range(1, 4):
        contact = EmergencyContact(
            user_id=test_user.id,
            name=f"연락처{i}",
            contact_type="email",
            contact_value=f"contact{i}@example.com",
            priority=i
        )
        contacts.append(contact)
    
    db_session.add_all(contacts)
    db_session.commit()
    return contacts
```

---

## Fixture 사용 예시
```python
def test_something(client, auth_headers, test_user):
    # client, auth_headers, test_user가 자동 주입됨
    response = client.get("/api/v1/me", headers=auth_headers)
    assert response.json()["id"] == test_user.id


def test_with_data(client, auth_headers, three_contacts):
    # 이미 3개의 연락처가 있는 상태
    response = client.get("/api/v1/contacts", headers=auth_headers)
    assert response.json()["count"] == 3
```

## 완료 확인
- [ ] 필수 Fixture 정의
- [ ] 트랜잭션 롤백 설정
- [ ] 도메인별 Fixture 추가
- [ ] 테스트 격리 확인
