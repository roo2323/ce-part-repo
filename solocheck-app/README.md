# SoloCheck App

혼자 사는 사용자의 장기 미연락 상황을 감지하여, 사전 지정된 연락처에 자동 알림을 전달하는 모바일 서비스입니다.

## 기술 스택

- **Framework**: React Native + Expo
- **Language**: TypeScript
- **State Management**: Zustand
- **Navigation**: Expo Router
- **HTTP Client**: Axios
- **Form Validation**: react-hook-form + zod
- **Push Notifications**: Expo Notifications + FCM

## 시작하기

### 사전 요구사항

- Node.js 18.x 이상
- npm 또는 yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS: Xcode (macOS에서 개발 시)
- Android: Android Studio

### 설치

```bash
# 프로젝트 디렉토리로 이동
cd solocheck-app

# 의존성 설치
npm install

# 또는 yarn 사용 시
yarn install
```

### 환경 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 필요한 값 설정
```

### 실행

```bash
# Expo 개발 서버 시작
npm start

# iOS 시뮬레이터에서 실행
npm run ios

# Android 에뮬레이터에서 실행
npm run android

# 웹 브라우저에서 실행
npm run web
```

## 프로젝트 구조

```
solocheck-app/
├── app/                    # Expo Router 페이지
│   ├── (auth)/            # 인증 관련 화면
│   │   ├── _layout.tsx
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/            # 메인 탭 화면
│   │   ├── _layout.tsx
│   │   ├── index.tsx      # 홈 (체크인)
│   │   ├── contacts.tsx   # 비상연락처
│   │   ├── message.tsx    # 개인 메시지
│   │   └── settings.tsx   # 설정
│   ├── _layout.tsx        # 루트 레이아웃
│   └── index.tsx          # 진입점
├── components/            # 재사용 컴포넌트
│   ├── ui/               # 공통 UI 컴포넌트
│   ├── check-in/         # 체크인 관련 컴포넌트
│   └── contacts/         # 연락처 관련 컴포넌트
├── services/             # API 서비스
│   ├── api.ts            # Axios 인스턴스 및 인터셉터
│   ├── auth.service.ts   # 인증 API
│   ├── checkin.service.ts # 체크인 API
│   └── contacts.service.ts # 연락처 API
├── stores/               # Zustand 스토어
│   ├── auth.store.ts     # 인증 상태
│   └── checkin.store.ts  # 체크인 상태
├── hooks/                # 커스텀 훅
│   └── useAuth.ts
├── types/                # TypeScript 타입 정의
│   ├── index.ts          # 공통 타입
│   └── api.ts            # API 관련 타입
├── constants/            # 상수
│   └── index.ts
├── utils/                # 유틸리티 함수
│   └── index.ts
└── assets/               # 이미지, 폰트 등
```

## 주요 기능

1. **체크인**: 매일 체크인하여 안전을 알림
2. **비상연락처 관리**: 최대 3명의 비상연락처 등록
3. **개인 메시지**: 비상시 전달될 메시지 작성
4. **푸시 알림**: 체크인 리마인더 및 상태 알림

## 개발 명령어

```bash
# TypeScript 타입 체크
npm run typecheck

# ESLint 검사
npm run lint

# ESLint 자동 수정
npm run lint:fix
```

## 서비스 안내

> 본 서비스는 사망 여부를 확인하지 않습니다.
> 긴급 상황 시 112/119 등 공공기관에 연락하세요.
> 알림은 '연락 두절' 기준으로 발송됩니다.

## 라이선스

이 프로젝트는 비공개 프로젝트입니다.
