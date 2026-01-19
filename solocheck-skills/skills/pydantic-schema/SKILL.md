---
name: pydantic-schema
description: Pydantic 스키마 구현 시 사용. BACKEND_DEV 전용. 요청/응답 검증 스키마 작성.
---

# Pydantic 스키마 체크리스트

## 파일 구조
- [ ] `src/{module}/schemas.py` 위치
- [ ] Request/Response 분리

## 클래스 정의
- [ ] `BaseModel` 상속
- [ ] 클래스명 명확 (`Create{Resource}Request`, `{Resource}Response`)
- [ ] Docstring 작성

## 필드 정의
- [ ] Type Hints 필수
- [ ] `Field()` 사용하여 검증
- [ ] `description` 명시
- [ ] `min_length`, `max_length` 설정
- [ ] `ge`, `le` (숫자 범위) 설정

## 검증
- [ ] `@field_validator` 커스텀 검증 (필요 시)
- [ ] `Literal` 사용 (선택지 제한)
- [ ] `Optional` 사용 (선택 필드)

## 설정
- [ ] `model_config = {"from_attributes": True}` (ORM 변환용)
- [ ] `model_config = {"strict": True}` (엄격 모드, 선택)

---

## 스키마 템플릿
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal, Optional


class Create{Resource}Request(BaseModel):
    """리소스 생성 요청"""
    name: str = Field(..., min_length=1, max_length=50, description="이름")
    type: Literal["option1", "option2"] = Field(..., description="유형")
    value: str = Field(..., min_length=1, description="값")
    priority: int = Field(..., ge=1, le=3, description="우선순위 (1-3)")
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, v, info):
        # 커스텀 검증 로직
        if info.data.get("type") == "email" and "@" not in v:
            raise ValueError("올바른 이메일 형식이 아닙니다")
        return v
    
    model_config = {"strict": True}


class Update{Resource}Request(BaseModel):
    """리소스 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=3)


class {Resource}Response(BaseModel):
    """리소스 응답"""
    id: str
    name: str
    type: str
    value: str
    priority: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class {Resource}ListResponse(BaseModel):
    """리소스 목록 응답"""
    data: list[{Resource}Response]
    count: int
```

---

## 네이밍 컨벤션
| 용도 | 패턴 | 예시 |
|------|------|------|
| 생성 요청 | `Create{Resource}Request` | `CreateContactRequest` |
| 수정 요청 | `Update{Resource}Request` | `UpdateContactRequest` |
| 단일 응답 | `{Resource}Response` | `ContactResponse` |
| 목록 응답 | `{Resource}ListResponse` | `ContactListResponse` |

## 완료 확인
- [ ] SPEC.md API 명세와 일치
- [ ] 모든 필드 검증 적용
- [ ] Type Hints 적용
- [ ] Docstring 작성
