# SoloCheck Backend

1인 가구 안부 확인 서비스 백엔드 API

## 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 + Alembic
- **Database**: PostgreSQL 15
- **Queue**: Celery + Redis
- **Auth**: python-jose (JWT), passlib (bcrypt)
- **Email**: SendGrid
- **Push**: firebase-admin (FCM)

## 프로젝트 구조

```
solocheck-backend/
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI 앱 진입점
│   ├── config.py         # Pydantic Settings 설정
│   ├── database.py       # SQLAlchemy 설정
│   ├── auth/             # 인증 모듈
│   ├── users/            # 사용자 모듈
│   ├── checkin/          # 체크인 모듈
│   ├── contacts/         # 비상연락처 모듈
│   ├── messages/         # 메시지 모듈
│   ├── notifications/    # 알림 모듈
│   ├── scheduler/        # Celery 스케줄러
│   └── common/           # 공통 유틸리티
├── alembic/              # DB 마이그레이션
├── tests/                # 테스트
├── docker-compose.yml    # Docker 구성
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 시작하기

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd solocheck-backend

# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 수정 (필요시)
```

### 2. Docker를 사용한 실행 (권장)

```bash
# 모든 서비스 시작 (PostgreSQL, Redis, Backend, Celery)
docker-compose up -d

# 로그 확인
docker-compose logs -f backend

# 서비스 중지
docker-compose down
```

### 3. 로컬 개발 환경

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL, Redis 실행 (Docker)
docker-compose up -d db redis

# 개발 서버 실행
uvicorn src.main:app --reload --port 8000
```

## API 문서

서버 실행 후 아래 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 헬스 체크

```bash
# 기본 헬스 체크
curl http://localhost:8000/health

# API v1 헬스 체크
curl http://localhost:8000/api/v1/health
```

## 테스트

```bash
# 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 연결 URL | postgresql://solocheck:solocheck@localhost:5432/solocheck |
| REDIS_URL | Redis 연결 URL | redis://localhost:6379/0 |
| SECRET_KEY | JWT 서명 키 | (필수 설정) |
| FCM_CREDENTIALS_PATH | Firebase 인증 파일 경로 | - |
| SENDGRID_API_KEY | SendGrid API 키 | - |
