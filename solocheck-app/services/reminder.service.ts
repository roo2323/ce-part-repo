import { api, getErrorMessage } from './api';
import type { ReminderSettings, UpdateReminderSettingsRequest } from '@/types';

// API Response types (snake_case from backend)
interface ReminderSettingsApiResponse {
  id: string;
  user_id: string;
  reminder_hours_before: number[];
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  preferred_time: string | null;
  push_enabled: boolean;
  email_enabled: boolean;
  custom_message: string | null;
}

interface ReminderSettingsUpdateApiResponse {
  message: string;
  settings: ReminderSettingsApiResponse;
}

// Transform API response to frontend format
const transformSettings = (data: ReminderSettingsApiResponse): ReminderSettings => ({
  id: data.id,
  userId: data.user_id,
  reminderHoursBefore: data.reminder_hours_before,
  quietHoursStart: data.quiet_hours_start,
  quietHoursEnd: data.quiet_hours_end,
  preferredTime: data.preferred_time,
  pushEnabled: data.push_enabled,
  emailEnabled: data.email_enabled,
  customMessage: data.custom_message,
});

export const reminderService = {
  /**
   * Get reminder settings for the current user
   */
  async getSettings(): Promise<ReminderSettings> {
    try {
      const response = await api.get<ReminderSettingsApiResponse>('/settings/reminder');
      return transformSettings(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update reminder settings
   */
  async updateSettings(data: UpdateReminderSettingsRequest): Promise<ReminderSettings> {
    try {
      const response = await api.put<ReminderSettingsUpdateApiResponse>('/settings/reminder', data);
      return transformSettings(response.data.settings);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Clear quiet hours settings
   */
  async clearQuietHours(): Promise<ReminderSettings> {
    try {
      const response = await api.delete<ReminderSettingsUpdateApiResponse>('/settings/reminder/quiet-hours');
      return transformSettings(response.data.settings);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default reminderService;
