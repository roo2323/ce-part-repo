---
name: jwt-auth
description: JWT 인증 구현 시 사용. BACKEND_DEV 전용. Access/Refresh Token 생성 및 검증.
---

# JWT 인증 구현 체크리스트

## 파일 구조
- [ ] `src/common/security.py` - 토큰 생성/검증
- [ ] `src/auth/dependencies.py` - 인증 의존성
- [ ] `src/auth/router.py` - 인증 API
- [ ] `src/auth/service.py` - 인증 서비스

## 토큰 설정
- [ ] SECRET_KEY 환경변수 사용
- [ ] Access Token 만료: 15분
- [ ] Refresh Token 만료: 7일
- [ ] 알고리즘: HS256

## 토큰 Payload
- [ ] `sub`: user_id
- [ ] `exp`: 만료 시간
- [ ] `type`: "access" 또는 "refresh"

## 비밀번호
- [ ] bcrypt 해싱 사용
- [ ] `passlib.context.CryptContext` 사용

---

## security.py 템플릿
```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호를 해싱합니다."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Access Token을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    """Refresh Token을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """토큰을 디코딩합니다."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
```

## dependencies.py 템플릿
```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database import get_db
from src.common.security import decode_token
from src.users.models import User
from src.common.exceptions import AuthException

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """현재 인증된 사용자를 반환합니다."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise AuthException(code="AUTH004", message="유효하지 않은 토큰입니다")
    
    if payload.get("type") != "access":
        raise AuthException(code="AUTH004", message="유효하지 않은 토큰입니다")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if not user:
        raise AuthException(code="USER001", message="사용자를 찾을 수 없습니다")
    
    return user
```

---

## 완료 확인
- [ ] 토큰 생성 구현
- [ ] 토큰 검증 구현
- [ ] 비밀번호 해싱 구현
- [ ] 인증 의존성 구현
- [ ] 테스트 코드 작성
