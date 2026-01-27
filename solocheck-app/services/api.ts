import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Platform-specific storage helpers
const storage = {
  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    }
    return SecureStore.getItemAsync(key);
  },

  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },

  async removeItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

// Token management functions
export const tokenManager = {
  async getAccessToken(): Promise<string | null> {
    try {
      return await storage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },

  async setAccessToken(token: string): Promise<void> {
    await storage.setItem(TOKEN_KEY, token);
  },

  async getRefreshToken(): Promise<string | null> {
    try {
      return await storage.getItem(REFRESH_TOKEN_KEY);
    } catch {
      return null;
    }
  },

  async setRefreshToken(token: string): Promise<void> {
    await storage.setItem(REFRESH_TOKEN_KEY, token);
  },

  async clearTokens(): Promise<void> {
    await storage.removeItem(TOKEN_KEY);
    await storage.removeItem(REFRESH_TOKEN_KEY);
  },
};

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = await tokenManager.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await tokenManager.getRefreshToken();
        if (!refreshToken) {
          throw new Error('로그인이 필요합니다.');
        }

        // Try to refresh the token
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refreshToken,
        });

        const { accessToken, refreshToken: newRefreshToken } = response.data;

        await tokenManager.setAccessToken(accessToken);
        if (newRefreshToken) {
          await tokenManager.setRefreshToken(newRefreshToken);
        }

        // Retry the original request
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear tokens and reject
        await tokenManager.clearTokens();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Error response type
export interface ApiError {
  statusCode: number;
  message: string;
  error: string;
}

// 영어 에러 메시지 -> 한글 매핑
const errorMessageMap: Record<string, string> = {
  'Invalid credentials': '이메일 또는 비밀번호가 올바르지 않습니다.',
  'Invalid email or password': '이메일 또는 비밀번호가 올바르지 않습니다.',
  'User not found': '사용자를 찾을 수 없습니다.',
  'Email already registered': '이미 등록된 이메일입니다.',
  'Email already exists': '이미 등록된 이메일입니다.',
  'Token expired': '인증이 만료되었습니다. 다시 로그인해주세요.',
  'Invalid token': '인증이 유효하지 않습니다. 다시 로그인해주세요.',
  'No refresh token': '로그인이 필요합니다.',
  'Unauthorized': '로그인이 필요합니다.',
  'Not authenticated': '로그인이 필요합니다.',
  'Permission denied': '권한이 없습니다.',
  'Forbidden': '접근이 거부되었습니다.',
  'Not found': '요청한 정보를 찾을 수 없습니다.',
  'Internal server error': '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
  'Network Error': '네트워크 연결을 확인해주세요.',
  'timeout of': '서버 응답 시간이 초과되었습니다.',
  'Password must be at least 8 characters': '비밀번호는 8자 이상이어야 합니다.',
  'Invalid password': '현재 비밀번호가 올바르지 않습니다.',
  'Passwords do not match': '비밀번호가 일치하지 않습니다.',
};

// Helper to extract error message
export const getErrorMessage = (error: unknown): string => {
  let message = '알 수 없는 오류가 발생했습니다.';

  if (axios.isAxiosError(error)) {
    const apiError = error.response?.data as ApiError;
    message = apiError?.message || error.message || message;

    // HTTP 상태 코드별 기본 메시지
    if (error.response?.status === 401) {
      message = '이메일 또는 비밀번호가 올바르지 않습니다.';
    } else if (error.response?.status === 403) {
      message = '접근 권한이 없습니다.';
    } else if (error.response?.status === 404) {
      message = '요청한 정보를 찾을 수 없습니다.';
    } else if (error.response?.status === 500) {
      message = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  } else if (error instanceof Error) {
    message = error.message;
  }

  // 영어 메시지를 한글로 변환
  for (const [eng, kor] of Object.entries(errorMessageMap)) {
    if (message.toLowerCase().includes(eng.toLowerCase())) {
      return kor;
    }
  }

  return message;
};

export default api;
