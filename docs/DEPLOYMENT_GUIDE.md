# SoloCheck 상용 배포 가이드

## 개요

SoloCheck 앱을 iOS App Store와 Google Play Store에 배포하기 위한 전체 절차입니다.

---

## 1. 사전 준비 사항

### 1.1 개발자 계정

| 플랫폼 | 계정 | 비용 | 등록 URL |
|--------|------|------|----------|
| **iOS** | Apple Developer Program | $99/년 | https://developer.apple.com/programs/ |
| **Android** | Google Play Console | $25 (1회) | https://play.google.com/console |

### 1.2 필요 자료

| 항목 | iOS | Android | 비고 |
|------|-----|---------|------|
| 앱 이름 | SoloCheck | SoloCheck | 스토어에 표시될 이름 |
| 앱 아이콘 | 1024x1024 PNG | 512x512 PNG | 투명 배경 불가 (iOS) |
| 스크린샷 | 6.7", 6.5", 5.5" | 폰, 태블릿 | 각 디바이스별 필요 |
| 앱 설명 | 4000자 이내 | 4000자 이내 | 한국어/영어 |
| 개인정보처리방침 URL | 필수 | 필수 | 웹 호스팅 필요 |
| 지원 URL | 필수 | 선택 | 문의 페이지 |
| 마케팅 URL | 선택 | 선택 | 랜딩 페이지 |

---

## 2. iOS 배포 절차

### 2.1 Apple Developer 계정 설정

```
1. https://developer.apple.com 접속
2. "Account" 클릭 → Apple ID로 로그인
3. "Join the Apple Developer Program" 클릭
4. 개인/조직 선택 (개인 권장 for 1인 개발)
5. $99 결제 (연간)
6. 승인 대기 (24-48시간)
```

### 2.2 App Store Connect 앱 생성

```
1. https://appstoreconnect.apple.com 접속
2. "앱" → "+" → "신규 앱"
3. 정보 입력:
   - 플랫폼: iOS
   - 이름: SoloCheck
   - 기본 언어: 한국어
   - 번들 ID: com.solocheck.app
   - SKU: solocheck-app-001
```

### 2.3 인증서 및 프로비저닝 설정

EAS Build를 사용하면 자동 관리됩니다:

```bash
# EAS CLI 로그인
eas login

# 인증서 자동 생성 및 관리
eas credentials
```

### 2.4 EAS Build 설정

**eas.json 수정:**
```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "ios": {
        "autoIncrement": true,
        "buildConfiguration": "Release"
      },
      "android": {
        "autoIncrement": true,
        "buildType": "app-bundle"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",
        "ascAppId": "YOUR_APP_STORE_CONNECT_APP_ID"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json"
      }
    }
  }
}
```

### 2.5 iOS 빌드 및 제출

```bash
# 프로덕션 빌드
eas build --platform ios --profile production

# App Store에 제출
eas submit --platform ios --latest
```

### 2.6 App Store 심사 준비

**심사 정보 입력 (App Store Connect):**

1. **앱 정보**
   - 카테고리: 라이프스타일 또는 유틸리티
   - 연령 등급: 4+

2. **버전 정보**
   - 스크린샷 업로드
   - 앱 설명 작성
   - 키워드 입력
   - 지원 URL, 개인정보처리방침 URL

3. **앱 심사 정보**
   - 테스트 계정 제공 (로그인 필요시)
   - 심사 메모 작성

4. **심사 제출**
   - "심사를 위해 제출" 클릭

**예상 심사 기간:** 24시간 ~ 7일

---

## 3. Android 배포 절차

### 3.1 Google Play Console 계정 설정

```
1. https://play.google.com/console 접속
2. Google 계정으로 로그인
3. "개발자 계정 만들기"
4. $25 등록비 결제 (1회성)
5. 개발자 정보 입력
```

### 3.2 앱 생성

```
1. Google Play Console → "앱 만들기"
2. 정보 입력:
   - 앱 이름: SoloCheck
   - 기본 언어: 한국어
   - 앱/게임: 앱
   - 무료/유료: 무료
3. 선언 동의 체크
```

### 3.3 스토어 등록정보 설정

**필수 입력 항목:**

| 항목 | 내용 |
|------|------|
| 앱 이름 | SoloCheck |
| 간단한 설명 | 혼자 사는 분들을 위한 안심 체크인 서비스 (80자 이내) |
| 자세한 설명 | 앱 기능 상세 설명 (4000자 이내) |
| 앱 아이콘 | 512x512 PNG |
| 그래픽 이미지 | 1024x500 PNG |
| 스크린샷 | 최소 2장, 권장 8장 |
| 카테고리 | 라이프스타일 |

### 3.4 콘텐츠 등급 설정

```
1. "콘텐츠 등급" 메뉴
2. 설문지 작성 (폭력성, 성적 콘텐츠 등)
3. SoloCheck의 경우 대부분 "아니오"
4. 예상 등급: 전체이용가
```

### 3.5 앱 서명 설정

**Google Play 앱 서명 사용 (권장):**
```bash
# EAS에서 자동 처리
eas build --platform android --profile production
```

### 3.6 Android 빌드 및 제출

```bash
# 프로덕션 빌드 (AAB 형식)
eas build --platform android --profile production

# Google Play에 제출
eas submit --platform android --latest
```

### 3.7 출시 트랙 선택

| 트랙 | 용도 | 권장 |
|------|------|------|
| 내부 테스트 | 팀 내부 테스트 (100명) | 초기 테스트 |
| 비공개 테스트 | 선택된 사용자 테스트 | 베타 테스트 |
| 공개 테스트 | 누구나 참여 가능 | 오픈 베타 |
| 프로덕션 | 정식 출시 | 최종 배포 |

**권장 순서:** 내부 테스트 → 비공개 테스트 → 프로덕션

---

## 4. 환경 변수 및 설정

### 4.1 프로덕션 환경 변수

**.env.production:**
```env
API_URL=https://api.solocheck.app/api/v1
```

### 4.2 app.config.js 수정

```javascript
export default {
  expo: {
    name: 'SoloCheck',
    slug: 'solocheck',
    version: '1.0.0',
    // ... 기존 설정
    extra: {
      apiUrl: process.env.API_URL || 'https://api.solocheck.app/api/v1',
      eas: {
        projectId: '77b0b694-bb37-4ddf-999e-3e7b9f157ce0',
      },
    },
  },
};
```

---

## 5. 백엔드 배포

### 5.1 서버 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| CPU | 1 vCPU | 2 vCPU |
| RAM | 1GB | 2GB |
| Storage | 20GB SSD | 50GB SSD |
| OS | Ubuntu 22.04 | Ubuntu 22.04 |

### 5.2 권장 호스팅

| 서비스 | 월 비용 | 특징 |
|--------|---------|------|
| AWS EC2 | ~$10+ | 가장 유연함 |
| DigitalOcean | ~$6+ | 간편한 설정 |
| Render | ~$7+ | 자동 배포 |
| Railway | ~$5+ | 가장 간편 |

### 5.3 필수 인프라

```
1. PostgreSQL 데이터베이스
2. Redis (Celery용)
3. 도메인 및 SSL 인증서
4. SendGrid 계정 (이메일)
5. Firebase 프로젝트 (FCM 푸시)
```

---

## 6. 체크리스트

### 6.1 배포 전 체크리스트

**공통:**
- [ ] 앱 아이콘 준비 (1024x1024, 512x512)
- [ ] 스크린샷 준비 (각 디바이스 크기별)
- [ ] 앱 설명 작성 (한국어, 영어)
- [ ] 개인정보처리방침 페이지 생성
- [ ] 백엔드 서버 배포 완료
- [ ] 프로덕션 API URL 설정

**iOS:**
- [ ] Apple Developer 계정 등록 ($99/년)
- [ ] App Store Connect 앱 생성
- [ ] EAS credentials 설정

**Android:**
- [ ] Google Play Console 계정 등록 ($25)
- [ ] 앱 생성 및 스토어 등록정보 입력
- [ ] 콘텐츠 등급 설정

### 6.2 심사 통과 팁

**iOS 심사 주의사항:**
1. 로그인이 필요한 경우 테스트 계정 필수 제공
2. 푸시 알림 권한 요청 시 사유 명시
3. 위치 정보 사용 시 목적 명시 (Info.plist)
4. 개인정보처리방침 URL 필수

**Android 심사 주의사항:**
1. 타겟 API 레벨 최신 유지 (현재 34 이상)
2. 민감한 권한 사용 시 설명 필수
3. 데이터 보안 섹션 작성 필수

---

## 7. 예상 일정

| 단계 | iOS | Android |
|------|-----|---------|
| 계정 생성 | 1-2일 | 즉시 |
| 앱 정보 입력 | 1일 | 1일 |
| 빌드 | 30분 | 30분 |
| 심사 | 1-7일 | 1-3일 |
| **총 예상** | **3-10일** | **2-5일** |

---

## 8. 비용 요약

### 초기 비용

| 항목 | 비용 |
|------|------|
| Apple Developer | $99/년 |
| Google Play | $25 (1회) |
| **합계** | **~$124** |

### 월간 운영 비용 (예상)

| 항목 | 비용 |
|------|------|
| 서버 (기본) | $10-20/월 |
| 도메인 | $1-2/월 |
| SendGrid (무료 티어) | $0 |
| Firebase (무료 티어) | $0 |
| **합계** | **~$15-25/월** |

---

## 9. 빠른 시작 명령어

```bash
# 1. EAS 로그인
eas login

# 2. 프로덕션 빌드 (iOS + Android 동시)
eas build --platform all --profile production

# 3. 스토어 제출
eas submit --platform ios --latest
eas submit --platform android --latest
```

---

## 10. 문의 및 지원

- Expo 문서: https://docs.expo.dev
- EAS Build 문서: https://docs.expo.dev/build/introduction/
- App Store 심사 가이드라인: https://developer.apple.com/app-store/review/guidelines/
- Google Play 정책: https://play.google.com/console/about/guides/releasewithconfidence/
