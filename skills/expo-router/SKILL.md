---
name: expo-router
description: Expo Router 네비게이션 구현 시 사용. FRONTEND_DEV 전용. 라우팅 및 레이아웃 설정.
---

# Expo Router 네비게이션 체크리스트

## 파일 구조
- [ ] `app/_layout.tsx` - 루트 레이아웃
- [ ] `app/(auth)/_layout.tsx` - 인증 그룹 레이아웃
- [ ] `app/(tabs)/_layout.tsx` - 탭 그룹 레이아웃
- [ ] `app/(auth)/login.tsx` - 로그인 화면
- [ ] `app/(tabs)/home.tsx` - 홈 화면

## 라우트 그룹
- [ ] `(auth)`: 비로그인 사용자용
- [ ] `(tabs)`: 로그인 사용자용 (탭 네비게이션)

## 인증 가드
- [ ] 로그인 상태에 따라 리다이렉트
- [ ] `useAuthStore` 활용
- [ ] `isLoading` 상태 처리

## 네비게이션 훅
- [ ] `useRouter`: 프로그래매틱 네비게이션
- [ ] `useSegments`: 현재 경로 세그먼트
- [ ] `useFocusEffect`: 화면 포커스 이벤트
- [ ] `useLocalSearchParams`: URL 파라미터

---

## 루트 레이아웃 템플릿
```tsx
// app/_layout.tsx
import { useEffect } from 'react';
import { Slot, useRouter, useSegments } from 'expo-router';
import { useAuthStore } from '@/stores/auth.store';

export default function RootLayout() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      // 로그인 필요
      router.replace('/login');
    } else if (isAuthenticated && inAuthGroup) {
      // 이미 로그인됨
      router.replace('/home');
    }
  }, [isAuthenticated, isLoading, segments]);

  return <Slot />;
}
```

## 탭 레이아웃 템플릿
```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#4F46E5',
        tabBarInactiveTintColor: '#6B7280',
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: '홈',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="contacts"
        options={{
          title: '연락처',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="people" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: '설정',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

## 네비게이션 사용 예시
```tsx
import { useRouter } from 'expo-router';

function SomeScreen() {
  const router = useRouter();
  
  const goToDetail = (id: string) => {
    router.push(`/detail/${id}`);
  };
  
  const goBack = () => {
    router.back();
  };
  
  const replaceToHome = () => {
    router.replace('/home');
  };
  
  return (/* ... */);
}
```

---

## 완료 확인
- [ ] 루트 레이아웃 구현
- [ ] 인증 가드 구현
- [ ] 탭 레이아웃 구현
- [ ] 네비게이션 동작 확인
