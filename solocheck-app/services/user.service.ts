import { api, getErrorMessage } from './api';
import type { User } from '@/types';

// Update user request type
export interface UpdateUserRequest {
  name?: string;
  phone?: string;
}

// Update FCM token request type
export interface UpdateFCMTokenRequest {
  fcm_token: string;
}

// Delete account request type
export interface DeleteAccountRequest {
  password: string;
}

// User response type
export interface UserResponse {
  user: User;
}

export const userService = {
  /**
   * Get current user profile (GET /users/me)
   */
  async getMe(): Promise<User> {
    try {
      const response = await api.get<UserResponse>('/users/me');
      return response.data.user;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update current user profile (PUT /users/me)
   */
  async updateMe(data: UpdateUserRequest): Promise<User> {
    try {
      const response = await api.put<UserResponse>('/users/me', data);
      return response.data.user;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update FCM token for push notifications (PUT /users/me/fcm-token)
   */
  async updateFCMToken(fcmToken: string): Promise<void> {
    try {
      await api.put('/users/me/fcm-token', { fcm_token: fcmToken });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Delete user account (DELETE /users/me)
   */
  async deleteMe(password: string): Promise<void> {
    try {
      await api.delete('/users/me', { data: { password } });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default userService;
