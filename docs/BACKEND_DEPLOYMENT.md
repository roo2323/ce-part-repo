# SoloCheck 백엔드 배포 가이드 (Railway)

## 왜 Railway인가?

| 서비스 | 장점 | 단점 | 월 비용 |
|--------|------|------|---------|
| **Railway** | 가장 간편, GitHub 연동 | 무료 티어 제한 | ~$5-10 |
| Render | 무료 티어 있음 | 콜드 스타트 지연 | ~$7+ |
| DigitalOcean | 안정적 | 설정 복잡 | ~$12+ |
| AWS | 가장 유연 | 가장 복잡 | ~$15+ |

**Railway 선택 이유:** GitHub 연동으로 자동 배포, PostgreSQL/Redis 원클릭 추가

---

## 1. 사전 준비

### 1.1 필요한 계정
- GitHub 계정 (코드 저장소)
- Railway 계정 (https://railway.app)

### 1.2 프로젝트 구조 확인
```
solocheck-backend/
├── src/
├── alembic/
├── requirements.txt
├── Dockerfile          # 생성 필요
├── railway.toml        # 생성 필요
└── .env.example
```

---

## 2. 배포 파일 생성

### 2.1 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# 포트
EXPOSE 8000

# 실행
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 railway.toml
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### 2.3 .env.example 업데이트
```env
# Database (Railway에서 자동 제공)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (Railway에서 자동 제공)
REDIS_URL=redis://host:6379

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SendGrid (이메일)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@solocheck.app

# Firebase (푸시 알림)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email

# App
APP_ENV=production
DEBUG=false
```

---

## 3. Railway 배포 단계

### Step 1: Railway 프로젝트 생성

```
1. https://railway.app 접속
2. GitHub로 로그인
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택
5. solocheck-backend 저장소 선택
```

### Step 2: PostgreSQL 추가

```
1. 프로젝트 대시보드에서 "+ New" 클릭
2. "Database" → "PostgreSQL" 선택
3. 자동으로 DATABASE_URL 환경변수 연결됨
```

### Step 3: Redis 추가

```
1. "+ New" 클릭
2. "Database" → "Redis" 선택
3. 자동으로 REDIS_URL 환경변수 연결됨
```

### Step 4: 환경 변수 설정

```
1. Backend 서비스 클릭
2. "Variables" 탭
3. 다음 변수들 추가:

JWT_SECRET_KEY=<32자 이상 랜덤 문자열>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=production
DEBUG=false

# SendGrid (나중에 설정 가능)
SENDGRID_API_KEY=<SendGrid API 키>
FROM_EMAIL=noreply@solocheck.app

# Firebase (나중에 설정 가능)
FIREBASE_PROJECT_ID=<Firebase 프로젝트 ID>
```

### Step 5: 도메인 설정

```
1. Backend 서비스 → "Settings" 탭
2. "Networking" → "Generate Domain" 클릭
3. Railway 제공 도메인: xxx.up.railway.app
4. (선택) 커스텀 도메인 연결
```

### Step 6: 배포 확인

```
1. "Deployments" 탭에서 빌드 로그 확인
2. 성공 시 URL 접속: https://xxx.up.railway.app/docs
3. FastAPI Swagger UI 확인
```

---

## 4. 데이터베이스 마이그레이션

### Railway CLI 설치 (선택)

```bash
# macOS
brew install railway

# 또는 npm
npm install -g @railway/cli
```

### 마이그레이션 실행

**방법 1: Railway CLI**
```bash
# 로그인
railway login

# 프로젝트 연결
railway link

# 마이그레이션 실행
railway run alembic upgrade head
```

**방법 2: Dockerfile에 포함**
```dockerfile
# 시작 스크립트 사용
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 5. Celery Worker 배포

### Step 1: 별도 서비스 생성

```
1. 프로젝트 대시보드 → "+ New"
2. "Empty Service" 선택
3. 이름: "celery-worker"
```

### Step 2: 설정

```
1. "Settings" → "Source"
2. 같은 GitHub 저장소 연결
3. "Settings" → "Build"
4. Start Command 설정:
   celery -A src.scheduler.tasks worker --loglevel=info
```

### Step 3: Celery Beat (스케줄러)

```
1. 또 다른 서비스 생성: "celery-beat"
2. Start Command:
   celery -A src.scheduler.tasks beat --loglevel=info
```

---

## 6. 최종 아키텍처

```
Railway Project
├── Backend API (FastAPI)     ← 메인 서비스
│   └── https://api.solocheck.app
├── PostgreSQL               ← 데이터베이스
├── Redis                    ← Celery 브로커
├── Celery Worker            ← 백그라운드 작업
└── Celery Beat              ← 스케줄러
```

---

## 7. 비용 예상 (Railway)

| 서비스 | 예상 비용 |
|--------|----------|
| Backend API | ~$2-3/월 |
| PostgreSQL | ~$2-3/월 |
| Redis | ~$1-2/월 |
| Celery Worker | ~$2-3/월 |
| Celery Beat | ~$1-2/월 |
| **총합** | **~$8-13/월** |

*사용량에 따라 변동. Hobby Plan $5/월부터 시작*

---

## 8. 배포 체크리스트

### 필수
- [ ] GitHub에 solocheck-backend 저장소 생성/푸시
- [ ] Dockerfile 생성
- [ ] railway.toml 생성
- [ ] Railway 프로젝트 생성
- [ ] PostgreSQL 추가
- [ ] Redis 추가
- [ ] 환경 변수 설정
- [ ] 마이그레이션 실행
- [ ] API 동작 확인 (/docs, /health)

### 선택 (나중에)
- [ ] 커스텀 도메인 연결
- [ ] SendGrid 설정 (이메일)
- [ ] Firebase 설정 (푸시 알림)
- [ ] Celery Worker/Beat 추가

---

## 9. 빠른 시작

```bash
# 1. GitHub 저장소 푸시 (이미 있다면 스킵)
cd solocheck-backend
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/solocheck-backend.git
git push -u origin main

# 2. Railway CLI로 배포 (선택적)
railway login
railway init
railway up
```

---

## 10. 트러블슈팅

### 빌드 실패
```
- requirements.txt에 모든 의존성 있는지 확인
- Python 버전 확인 (3.11 권장)
```

### DB 연결 실패
```
- DATABASE_URL 환경변수 확인
- PostgreSQL 서비스가 같은 프로젝트에 있는지 확인
```

### 마이그레이션 실패
```
- alembic/versions/ 폴더 확인
- 마이그레이션 순서 확인 (down_revision)
```

---

## 다음 단계

배포 완료 후:
1. 앱의 API_URL을 Railway 도메인으로 변경
2. 실제 기기에서 테스트
3. 필요시 커스텀 도메인 연결
