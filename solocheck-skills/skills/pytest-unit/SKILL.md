---
name: pytest-unit
description: pytest 단위 테스트 작성 시 사용. QA 전용. Service Layer 테스트.
---

# pytest 단위 테스트 체크리스트

## 파일 구조
- [ ] `tests/test_{module}_service.py` 위치
- [ ] 클래스별로 테스트 그룹화

## 테스트 함수 네이밍
- [ ] `test_` 접두사 필수
- [ ] 동작_조건_결과 형식
- [ ] 예: `test_create_contact_success`
- [ ] 예: `test_create_contact_max_limit_exceeded`

## 테스트 패턴
- [ ] Arrange-Act-Assert (AAA)
- [ ] Given-When-Then

## Mock 사용
- [ ] `unittest.mock.Mock` 사용
- [ ] DB 세션 Mock
- [ ] 외부 서비스 Mock

## Fixture 활용
- [ ] `@pytest.fixture` 사용
- [ ] 공통 Fixture는 `conftest.py`

---

## 단위 테스트 템플릿
```python
import pytest
from unittest.mock import Mock, MagicMock
from src.{module} import service
from src.{module}.schemas import Create{Resource}Request
from src.common.exceptions import NotFoundException, DuplicateError


class TestCreate{Resource}:
    """create_{resource} 서비스 단위 테스트"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock DB 세션"""
        db = Mock()
        db.query.return_value.filter.return_value = Mock()
        return db
    
    @pytest.fixture
    def valid_request(self):
        """유효한 요청 데이터"""
        return Create{Resource}Request(
            name="테스트",
            value="test@example.com",
            priority=1
        )
    
    # --- 정상 케이스 ---
    
    def test_create_{resource}_success(self, mock_db, valid_request):
        """정상 생성 케이스"""
        # Arrange
        mock_db.query().filter().count.return_value = 0
        mock_db.query().filter().first.return_value = None
        
        # Act
        result = service.create_{resource}(mock_db, "user_123", valid_request)
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    # --- 에러 케이스 ---
    
    def test_create_{resource}_duplicate(self, mock_db, valid_request):
        """중복 데이터 케이스"""
        # Arrange
        mock_db.query().filter().count.return_value = 1
        mock_db.query().filter().first.return_value = Mock()  # 기존 데이터 존재
        
        # Act & Assert
        with pytest.raises(DuplicateError) as exc:
            service.create_{resource}(mock_db, "user_123", valid_request)
        
        assert exc.value.code == "{RESOURCE}002"
        mock_db.add.assert_not_called()


class TestGet{Resource}:
    """get_{resource} 서비스 단위 테스트"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    def test_get_{resource}_success(self, mock_db):
        """정상 조회 케이스"""
        # Arrange
        mock_item = Mock(id="item_123")
        mock_db.query().filter().first.return_value = mock_item
        
        # Act
        result = service.get_{resource}(mock_db, "user_123", "item_123")
        
        # Assert
        assert result.id == "item_123"
    
    def test_get_{resource}_not_found(self, mock_db):
        """없는 데이터 조회 케이스"""
        # Arrange
        mock_db.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc:
            service.get_{resource}(mock_db, "user_123", "nonexistent")
        
        assert exc.value.code == "{RESOURCE}003"
```

## 실행 명령어
```bash
# 전체 테스트
pytest tests/ -v

# 특정 파일
pytest tests/test_contacts_service.py -v

# 특정 클래스
pytest tests/test_contacts_service.py::TestCreateContact -v

# 특정 테스트
pytest tests/test_contacts_service.py::TestCreateContact::test_create_contact_success -v
```

---

## 완료 확인
- [ ] 정상 케이스 테스트
- [ ] 에러 케이스 테스트
- [ ] Mock 적절히 사용
- [ ] 테스트 통과 확인
