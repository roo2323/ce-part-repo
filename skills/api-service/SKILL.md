---
name: api-service
description: React Native API 서비스 레이어 구현 시 사용. FRONTEND_DEV 전용. Axios 기반 API 호출.
---

# API 서비스 체크리스트

## 파일 구조
- [ ] `services/api.ts` - Axios 인스턴스 (공통)
- [ ] `services/{resource}.service.ts` - 도메인별 서비스

## Axios 인스턴스
- [ ] baseURL 설정
- [ ] timeout 설정
- [ ] 요청 인터셉터: 토큰 추가
- [ ] 응답 인터셉터: 토큰 갱신

## 서비스 함수
- [ ] async/await 사용
- [ ] 타입 정의 적용
- [ ] 에러 처리는 호출측에서

## TypeScript
- [ ] 요청/응답 타입 import
- [ ] 제네릭 활용

---

## api.ts 템플릿
```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '@/stores/auth.store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 토큰 추가
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 토큰 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');
        
        const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        await AsyncStorage.setItem('access_token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

## {resource}.service.ts 템플릿
```typescript
import { api } from './api';
import type {
  {Resource},
  {Resource}ListResponse,
  Create{Resource}Request,
  Update{Resource}Request,
} from '@/types/{resource}';

export const {resource}Service = {
  async getAll(): Promise<{Resource}ListResponse> {
    const response = await api.get<{Resource}ListResponse>('/api/v1/{resources}');
    return response.data;
  },

  async getById(id: string): Promise<{Resource}> {
    const response = await api.get<{Resource}>(`/api/v1/{resources}/${id}`);
    return response.data;
  },

  async create(data: Create{Resource}Request): Promise<{Resource}> {
    const response = await api.post<{Resource}>('/api/v1/{resources}', data);
    return response.data;
  },

  async update(id: string, data: Update{Resource}Request): Promise<{Resource}> {
    const response = await api.put<{Resource}>(`/api/v1/{resources}/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/{resources}/${id}`);
  },
};
```

---

## 완료 확인
- [ ] Axios 인스턴스 설정
- [ ] 토큰 인터셉터 구현
- [ ] 도메인 서비스 구현
- [ ] TypeScript 타입 적용
