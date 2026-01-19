---
name: zustand-store
description: Zustand 전역 상태 관리 구현 시 사용. FRONTEND_DEV 전용. 스토어 생성 및 영속화.
---

# Zustand 스토어 체크리스트

## 파일 구조
- [ ] `stores/{domain}.store.ts` 위치
- [ ] 도메인별 스토어 분리

## 스토어 구조
- [ ] 상태 (State) 정의
- [ ] 액션 (Actions) 정의
- [ ] 타입 인터페이스 정의

## 영속화 (persist)
- [ ] `AsyncStorage` 사용 (React Native)
- [ ] `partialize`: 영속화할 상태만 선택
- [ ] `name`: 스토리지 키 이름

## TypeScript
- [ ] State 인터페이스 정의
- [ ] 제네릭 타입 적용

---

## 기본 스토어 템플릿
```typescript
import { create } from 'zustand';

interface {Domain}State {
  // 상태
  data: {Type} | null;
  isLoading: boolean;
  
  // 액션
  setData: (data: {Type}) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

export const use{Domain}Store = create<{Domain}State>((set) => ({
  // 초기 상태
  data: null,
  isLoading: false,
  
  // 액션
  setData: (data) => set({ data }),
  setLoading: (isLoading) => set({ isLoading }),
  reset: () => set({ data: null, isLoading: false }),
}));
```

## 영속화 스토어 템플릿 (Auth 예시)
```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { User } from '@/types/user';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  setUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: true,
        isLoading: false,
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => {
        AsyncStorage.multiRemove(['access_token', 'refresh_token']);
        set({ user: null, isAuthenticated: false, isLoading: false });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
```

## 사용 예시
```tsx
import { useAuthStore } from '@/stores/auth.store';

function ProfileScreen() {
  const { user, logout } = useAuthStore();
  
  return (
    <View>
      <Text>{user?.nickname}</Text>
      <Button title="로그아웃" onPress={logout} />
    </View>
  );
}
```

---

## 완료 확인
- [ ] State 인터페이스 정의
- [ ] 액션 함수 구현
- [ ] 영속화 설정 (필요 시)
- [ ] TypeScript 타입 적용
