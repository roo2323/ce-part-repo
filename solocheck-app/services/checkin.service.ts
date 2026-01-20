import { api, getErrorMessage } from './api';
import type { CheckIn, CheckInResponse, CheckInHistoryResponse } from '@/types';

// Check-in settings request type
export interface CheckInSettingsRequest {
  checkin_cycle_days: number;
  grace_period_hours: number;
}

// Check-in status response type
export interface CheckInStatusResponse {
  last_checkin: CheckIn | null;
  checkin_cycle_days: number;
  grace_period_hours: number;
  next_checkin_due: string | null;
  days_remaining: number | null;
  hours_since_last_checkin: number | null;
  is_overdue: boolean;
}

export const checkinService = {
  /**
   * Perform a check-in
   */
  async checkIn(): Promise<CheckIn> {
    try {
      const response = await api.post<CheckInResponse>('/checkins');
      return response.data.checkin;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get the last check-in
   */
  async getLastCheckIn(): Promise<CheckIn | null> {
    try {
      const response = await api.get<CheckIn>('/checkins/last');
      return response.data;
    } catch (error) {
      // If 404, no check-ins exist yet
      if ((error as any)?.response?.status === 404) {
        return null;
      }
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get check-in history with pagination
   */
  async getHistory(page = 1, limit = 20): Promise<CheckInHistoryResponse> {
    try {
      const response = await api.get<CheckInHistoryResponse>('/checkins', {
        params: { page, limit },
      });
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get check-in status (GET /checkin/status)
   */
  async getStatus(): Promise<CheckInStatusResponse> {
    try {
      const response = await api.get<CheckInStatusResponse>('/checkin/status');
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update check-in settings (PUT /checkin/settings)
   */
  async updateSettings(data: CheckInSettingsRequest): Promise<void> {
    try {
      await api.put('/checkin/settings', data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default checkinService;
