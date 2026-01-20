import { api, tokenManager, getErrorMessage } from './api';
import type { User } from '@/types';
import type {
  RegisterRequest,
  LoginRequest,
  LoginResponse,
  RegisterResponse,
  RefreshTokenResponse,
  ForgotPasswordRequest,
} from '@/types/api';

export const authService = {
  /**
   * Register a new user
   * POST /api/v1/auth/register
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await api.post<RegisterResponse>('/auth/register', data);
      const { access_token, refresh_token } = response.data;

      // Store tokens
      await tokenManager.setAccessToken(access_token);
      await tokenManager.setRefreshToken(refresh_token);

      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Login with email and password
   * POST /api/v1/auth/login/json
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/auth/login/json', data);
      const { access_token, refresh_token } = response.data;

      // Store tokens
      await tokenManager.setAccessToken(access_token);
      await tokenManager.setRefreshToken(refresh_token);

      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Refresh access token
   * POST /api/v1/auth/refresh
   */
  async refresh(refreshToken: string): Promise<RefreshTokenResponse> {
    try {
      const response = await api.post<RefreshTokenResponse>('/auth/refresh', {
        refresh_token: refreshToken,
      });
      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Store new tokens
      await tokenManager.setAccessToken(access_token);
      if (newRefreshToken) {
        await tokenManager.setRefreshToken(newRefreshToken);
      }

      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Request password reset email
   * POST /api/v1/auth/forgot-password
   */
  async forgotPassword(email: string): Promise<void> {
    try {
      await api.post<{ message: string }>('/auth/forgot-password', { email } as ForgotPasswordRequest);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Logout - clear tokens
   */
  async logout(): Promise<void> {
    try {
      // Optionally call logout endpoint to invalidate token server-side
      await api.post('/auth/logout');
    } catch {
      // Ignore errors - we'll clear tokens anyway
    } finally {
      await tokenManager.clearTokens();
    }
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/users/me');
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Check if user is authenticated (has valid token)
   */
  async checkAuth(): Promise<User | null> {
    try {
      const token = await tokenManager.getAccessToken();
      if (!token) {
        return null;
      }
      return await this.getCurrentUser();
    } catch {
      await tokenManager.clearTokens();
      return null;
    }
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await api.patch<User>('/users/me', data);
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      await api.post('/auth/change-password', {
        currentPassword,
        newPassword,
      });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get stored tokens
   */
  async getStoredTokens(): Promise<{ accessToken: string | null; refreshToken: string | null }> {
    const accessToken = await tokenManager.getAccessToken();
    const refreshToken = await tokenManager.getRefreshToken();
    return { accessToken, refreshToken };
  },
};

export default authService;
