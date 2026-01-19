---
name: exception-handling
description: 커스텀 예외 처리 구현 시 사용. BACKEND_DEV 전용. 에러 코드 및 핸들러 작성.
---

# 커스텀 예외 처리 체크리스트

## 파일 구조
- [ ] `src/common/exceptions.py` - 예외 클래스 정의
- [ ] `src/main.py` - 글로벌 예외 핸들러 등록

## 예외 클래스 구조
- [ ] `AppException` 기본 클래스
- [ ] `code`: 에러 코드 (예: "AUTH001")
- [ ] `message`: 사용자 친화적 메시지
- [ ] `status_code`: HTTP 상태 코드

## 에러 코드 체계
- [ ] AUTH0XX: 인증 관련
- [ ] USER0XX: 사용자 관련
- [ ] CHECK0XX: 체크인 관련
- [ ] CONTACT0XX: 연락처 관련
- [ ] MSG0XX: 메시지 관련

## 에러 응답 형식
```json
{
  "code": "AUTH001",
  "message": "이메일 또는 비밀번호가 올바르지 않습니다"
}
```

---

## exceptions.py 템플릿
```python
from fastapi import HTTPException


class AppException(HTTPException):
    """애플리케이션 기본 예외"""
    
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message}
        )


class AuthException(AppException):
    """인증 관련 예외 (401)"""
    
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=401)


class NotFoundException(AppException):
    """리소스 없음 예외 (404)"""
    
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=404)


class DuplicateError(AppException):
    """중복 예외 (409)"""
    
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=409)


class MaxLimitExceededError(AppException):
    """최대 제한 초과 예외 (400)"""
    
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=400)


class ValidationError(AppException):
    """검증 실패 예외 (422)"""
    
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=422)
```

## main.py 핸들러 등록
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.common.exceptions import AppException

app = FastAPI()


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message}
    )
```

---

## 에러 코드 목록
| 코드 | HTTP | 메시지 |
|------|------|--------|
| AUTH001 | 401 | 이메일 또는 비밀번호가 올바르지 않습니다 |
| AUTH002 | 409 | 이미 사용 중인 이메일입니다 |
| AUTH003 | 401 | 토큰이 만료되었습니다 |
| AUTH004 | 401 | 유효하지 않은 토큰입니다 |
| USER001 | 404 | 사용자를 찾을 수 없습니다 |
| CONTACT001 | 400 | 비상연락처는 최대 3명까지 등록 가능합니다 |
| CONTACT002 | 409 | 이미 등록된 연락처입니다 |
| CONTACT003 | 404 | 연락처를 찾을 수 없습니다 |
| MSG001 | 400 | 메시지는 2000자 이내여야 합니다 |

## 완료 확인
- [ ] 예외 클래스 정의 완료
- [ ] 글로벌 핸들러 등록
- [ ] 에러 코드 목록 정리
- [ ] SPEC.md와 일치
