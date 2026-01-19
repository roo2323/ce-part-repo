---
name: fastapi-router
description: FastAPI 라우터 구현 시 사용. BACKEND_DEV 전용. API 엔드포인트 작성 체크리스트.
---

# FastAPI 라우터 체크리스트

## 파일 구조
- [ ] `src/{module}/router.py` 위치
- [ ] `main.py`에 라우터 등록

## 라우터 설정
- [ ] `APIRouter()` 사용
- [ ] `prefix="/api/v1/{resource}"` 설정
- [ ] `tags=["{Resource}"]` 설정

## 엔드포인트 정의
- [ ] HTTP 메서드 데코레이터 사용 (`@router.get`, `@router.post` 등)
- [ ] `response_model` 명시
- [ ] `status_code` 명시
- [ ] 함수명 동사_명사 형식 (`create_contact`, `get_contacts`)

## 의존성 주입
- [ ] `Depends(get_db)` - DB 세션
- [ ] `Depends(get_current_user)` - 인증 필요 시
- [ ] Type Hints 명시

## Docstring
- [ ] 함수 설명 작성
- [ ] Google 스타일 Docstring

---

## 라우터 템플릿
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth.dependencies import get_current_user
from src.users.models import User
from src.{module} import service
from src.{module}.schemas import (
    Create{Resource}Request,
    {Resource}Response,
    {Resource}ListResponse,
)

router = APIRouter(prefix="/api/v1/{resources}", tags=["{Resources}"])


@router.post("", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
def create_{resource}(
    request: Create{Resource}Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """리소스를 생성합니다."""
    return service.create_{resource}(db, current_user.id, request)


@router.get("", response_model={Resource}ListResponse)
def get_{resources}(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """리소스 목록을 조회합니다."""
    return service.get_{resources}(db, current_user.id)


@router.get("/{{{resource}_id}}", response_model={Resource}Response)
def get_{resource}(
    {resource}_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """단일 리소스를 조회합니다."""
    return service.get_{resource}(db, current_user.id, {resource}_id)


@router.put("/{{{resource}_id}}", response_model={Resource}Response)
def update_{resource}(
    {resource}_id: str,
    request: Update{Resource}Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """리소스를 수정합니다."""
    return service.update_{resource}(db, current_user.id, {resource}_id, request)


@router.delete("/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{resource}(
    {resource}_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """리소스를 삭제합니다."""
    service.delete_{resource}(db, current_user.id, {resource}_id)
```

---

## main.py 등록
```python
from src.{module}.router import router as {module}_router

app.include_router({module}_router)
```

## 완료 확인
- [ ] SPEC.md API 명세와 일치
- [ ] 모든 엔드포인트 구현
- [ ] Type Hints 적용
- [ ] 테스트 코드 작성 (QA 또는 직접)
