---
name: api-integration-test
description: FastAPI API 통합 테스트 작성 시 사용. QA 전용. TestClient 기반.
---

# API 통합 테스트 체크리스트

## 파일 구조
- [ ] `tests/test_{module}_api.py` 위치
- [ ] `tests/conftest.py` - 공통 Fixture

## TestClient 설정
- [ ] `fastapi.testclient.TestClient` 사용
- [ ] 테스트 DB 연결
- [ ] 의존성 오버라이드

## 테스트 항목
- [ ] 정상 응답 (200, 201, 204)
- [ ] 인증 실패 (401, 403)
- [ ] 검증 실패 (422)
- [ ] 비즈니스 에러 (400, 404, 409)

## Fixture 활용
- [ ] `client` - TestClient
- [ ] `auth_headers` - 인증 헤더
- [ ] `test_user` - 테스트 사용자
- [ ] 도메인별 테스트 데이터

---

## conftest.py 템플릿
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db
from src.users.models import User
from src.common.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    """테스트 DB 스키마 생성"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """각 테스트별 DB 세션 (롤백)"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """테스트 클라이언트"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """기본 테스트 사용자"""
    user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        nickname="테스트유저",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(test_user):
    """인증 헤더"""
    token = create_access_token({"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}
```

## API 통합 테스트 템플릿
```python
import pytest


class Test{Resource}API:
    """{Resource} API 통합 테스트"""
    
    # --- POST ---
    
    def test_create_{resource}_success(self, client, auth_headers):
        """생성 성공"""
        response = client.post(
            "/api/v1/{resources}",
            json={
                "name": "테스트",
                "value": "test@example.com",
                "priority": 1
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "테스트"
        assert "id" in data
    
    def test_create_{resource}_unauthorized(self, client):
        """인증 없이 생성 시도"""
        response = client.post(
            "/api/v1/{resources}",
            json={"name": "테스트", "value": "test@example.com", "priority": 1}
        )
        
        assert response.status_code == 403
    
    def test_create_{resource}_validation_error(self, client, auth_headers):
        """검증 실패"""
        response = client.post(
            "/api/v1/{resources}",
            json={"name": "", "priority": 10},  # 잘못된 값
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    # --- GET ---
    
    def test_get_{resources}_empty(self, client, auth_headers):
        """빈 목록 조회"""
        response = client.get("/api/v1/{resources}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
    
    # --- DELETE ---
    
    def test_delete_{resource}_success(self, client, auth_headers, existing_{resource}):
        """삭제 성공"""
        response = client.delete(
            f"/api/v1/{resources}/{existing_{resource}.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    def test_delete_{resource}_not_found(self, client, auth_headers):
        """없는 리소스 삭제"""
        response = client.delete(
            "/api/v1/{resources}/nonexistent-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
```

---

## 완료 확인
- [ ] conftest.py 설정 완료
- [ ] 모든 엔드포인트 테스트
- [ ] 정상/에러 케이스 모두 포함
- [ ] 테스트 통과 확인
