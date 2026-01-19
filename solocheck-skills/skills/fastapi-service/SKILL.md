---
name: fastapi-service
description: FastAPI Service Layer 구현 시 사용. BACKEND_DEV 전용. 비즈니스 로직 작성.
---

# Service Layer 체크리스트

## 파일 구조
- [ ] `src/{module}/service.py` 위치
- [ ] 함수 단위로 분리
- [ ] 비즈니스 로직만 담당 (API 호출 로직 분리)

## 함수 시그니처
- [ ] `db: Session` 첫 번째 매개변수
- [ ] Type Hints 필수
- [ ] 반환 타입 명시

## Docstring (Google 스타일)
- [ ] 함수 설명
- [ ] Args 섹션
- [ ] Returns 섹션
- [ ] Raises 섹션 (예외 발생 시)

## 예외 처리
- [ ] 커스텀 예외 사용 (`src/common/exceptions.py`)
- [ ] 에러 코드 명시
- [ ] 사용자 친화적 메시지

## 트랜잭션
- [ ] `db.commit()` 호출 (생성/수정/삭제)
- [ ] `db.refresh()` 호출 (생성/수정 후 반환)
- [ ] 에러 시 자동 롤백 (FastAPI가 처리)

---

## Service 템플릿
```python
from sqlalchemy.orm import Session
from src.{module}.models import {Model}
from src.{module}.schemas import (
    Create{Resource}Request,
    Update{Resource}Request,
    {Resource}ListResponse,
)
from src.common.exceptions import (
    NotFoundException,
    DuplicateError,
    MaxLimitExceededError,
)


def create_{resource}(
    db: Session,
    user_id: str,
    data: Create{Resource}Request
) -> {Model}:
    """리소스를 생성합니다.
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        data: 생성 요청 데이터
        
    Returns:
        생성된 {Model} 객체
        
    Raises:
        MaxLimitExceededError: 최대 등록 수 초과
        DuplicateError: 중복 데이터
    """
    # 비즈니스 규칙 검증
    # ...
    
    # 생성
    item = {Model}(
        user_id=user_id,
        **data.model_dump()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


def get_{resources}(db: Session, user_id: str) -> {Resource}ListResponse:
    """리소스 목록을 조회합니다."""
    items = db.query({Model}).filter(
        {Model}.user_id == user_id
    ).all()
    
    return {Resource}ListResponse(data=items, count=len(items))


def get_{resource}(db: Session, user_id: str, {resource}_id: str) -> {Model}:
    """단일 리소스를 조회합니다."""
    item = db.query({Model}).filter(
        {Model}.id == {resource}_id,
        {Model}.user_id == user_id
    ).first()
    
    if not item:
        raise NotFoundException(code="{CODE}001", message="리소스를 찾을 수 없습니다")
    
    return item


def update_{resource}(
    db: Session,
    user_id: str,
    {resource}_id: str,
    data: Update{Resource}Request
) -> {Model}:
    """리소스를 수정합니다."""
    item = get_{resource}(db, user_id, {resource}_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


def delete_{resource}(db: Session, user_id: str, {resource}_id: str) -> None:
    """리소스를 삭제합니다."""
    item = get_{resource}(db, user_id, {resource}_id)
    db.delete(item)
    db.commit()
```

---

## 완료 확인
- [ ] SPEC.md 비즈니스 규칙 구현
- [ ] 커스텀 예외 사용
- [ ] Type Hints 적용
- [ ] Docstring 작성
- [ ] 테스트 코드 작성
