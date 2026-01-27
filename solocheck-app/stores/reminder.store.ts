import { create } from 'zustand';
import { reminderService } from '@/services/reminder.service';
import type { ReminderSettings, UpdateReminderSettingsRequest } from '@/types';

interface ReminderState {
  settings: ReminderSettings | null;
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;
}

interface ReminderActions {
  fetchSettings: () => Promise<void>;
  updateSettings: (data: UpdateReminderSettingsRequest) => Promise<void>;
  clearQuietHours: () => Promise<void>;
  clearError: () => void;
}

type ReminderStore = ReminderState & ReminderActions;

const initialState: ReminderState = {
  settings: null,
  isLoading: false,
  isUpdating: false,
  error: null,
};

export const useReminderStore = create<ReminderStore>((set) => ({
  ...initialState,

  fetchSettings: async () => {
    set({ isLoading: true, error: null });
    try {
      const settings = await reminderService.getSettings();
      set({ settings, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '설정을 불러오는데 실패했습니다.',
      });
    }
  },

  updateSettings: async (data: UpdateReminderSettingsRequest) => {
    set({ isUpdating: true, error: null });
    try {
      const settings = await reminderService.updateSettings(data);
      set({ settings, isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : '설정 업데이트에 실패했습니다.',
      });
      throw error;
    }
  },

  clearQuietHours: async () => {
    set({ isUpdating: true, error: null });
    try {
      const settings = await reminderService.clearQuietHours();
      set({ settings, isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : '방해금지 시간 해제에 실패했습니다.',
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

export default useReminderStore;
