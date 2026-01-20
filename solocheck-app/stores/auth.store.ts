import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService } from '@/services/auth.service';
import { tokenManager } from '@/services/api';
import type { User } from '@/types';
import type { RegisterRequest } from '@/types/api';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nickname?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshTokens: () => Promise<void>;
  loadStoredAuth: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
  clearError: () => void;
  forgotPassword: (email: string) => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login({ email, password });
          const user = response.user
            ? {
                id: response.user.id,
                email: response.user.email,
                name: response.user.nickname || '',
                phone: '',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
              }
            : null;

          set({
            user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '로그인에 실패했습니다.',
          });
          throw error;
        }
      },

      register: async (email: string, password: string, nickname?: string) => {
        set({ isLoading: true, error: null });
        try {
          const registerData: RegisterRequest = { email, password };
          if (nickname) {
            registerData.nickname = nickname;
          }

          const response = await authService.register(registerData);
          const user: User = {
            id: response.id,
            email: response.email,
            name: response.nickname || '',
            phone: '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };

          set({
            user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '회원가입에 실패했습니다.',
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authService.logout();
        } finally {
          set({
            ...initialState,
            isLoading: false,
          });
        }
      },

      refreshTokens: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        try {
          const response = await authService.refresh(refreshToken);
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token || refreshToken,
          });
        } catch (error) {
          // Refresh failed, logout user
          await get().logout();
          throw error;
        }
      },

      loadStoredAuth: async () => {
        set({ isLoading: true });
        try {
          const tokens = await authService.getStoredTokens();

          if (tokens.accessToken) {
            // Verify token is still valid by fetching user
            try {
              const user = await authService.getCurrentUser();
              set({
                user,
                accessToken: tokens.accessToken,
                refreshToken: tokens.refreshToken,
                isAuthenticated: true,
                isLoading: false,
              });
            } catch {
              // Token invalid, try refresh
              if (tokens.refreshToken) {
                try {
                  await get().refreshTokens();
                  const user = await authService.getCurrentUser();
                  set({
                    user,
                    isAuthenticated: true,
                    isLoading: false,
                  });
                } catch {
                  // Refresh also failed
                  await tokenManager.clearTokens();
                  set({
                    ...initialState,
                    isLoading: false,
                  });
                }
              } else {
                await tokenManager.clearTokens();
                set({
                  ...initialState,
                  isLoading: false,
                });
              }
            }
          } else {
            set({
              ...initialState,
              isLoading: false,
            });
          }
        } catch {
          set({
            ...initialState,
            isLoading: false,
          });
        }
      },

      checkAuth: async () => {
        set({ isLoading: true });
        try {
          const user = await authService.checkAuth();
          if (user) {
            const tokens = await authService.getStoredTokens();
            set({
              user,
              accessToken: tokens.accessToken,
              refreshToken: tokens.refreshToken,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            set({
              user: null,
              accessToken: null,
              refreshToken: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } catch {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      forgotPassword: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          await authService.forgotPassword(email);
          set({ isLoading: false });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '비밀번호 재설정 요청에 실패했습니다.',
          });
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);

export default useAuthStore;
