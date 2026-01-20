import { create } from 'zustand';
import { checkinService, CheckInStatusResponse } from '@/services/checkin.service';
import type { CheckIn } from '@/types';

// Check-in status type for the store
export interface CheckInStatus {
  lastCheckin: CheckIn | null;
  checkinCycleDays: number;
  gracePeriodHours: number;
  nextCheckinDue: string | null;
  daysRemaining: number | null;
  hoursSinceLastCheckIn: number | null;
  isOverdue: boolean;
}

interface CheckinState {
  status: CheckInStatus | null;
  history: CheckIn[];
  isLoading: boolean;
  isUpdatingSettings: boolean;
  error: string | null;
}

interface CheckinActions {
  checkIn: () => Promise<void>;
  fetchStatus: () => Promise<void>;
  fetchHistory: (page?: number, limit?: number) => Promise<void>;
  updateSettings: (cycleDays: number, gracePeriodHours: number) => Promise<void>;
  clearError: () => void;
}

type CheckinStore = CheckinState & CheckinActions;

const initialState: CheckinState = {
  status: null,
  history: [],
  isLoading: false,
  isUpdatingSettings: false,
  error: null,
};

// Helper function to convert API response to store format
const mapStatusResponse = (response: CheckInStatusResponse): CheckInStatus => ({
  lastCheckin: response.last_checkin,
  checkinCycleDays: response.checkin_cycle_days,
  gracePeriodHours: response.grace_period_hours,
  nextCheckinDue: response.next_checkin_due,
  daysRemaining: response.days_remaining,
  hoursSinceLastCheckIn: response.hours_since_last_checkin,
  isOverdue: response.is_overdue,
});

export const useCheckinStore = create<CheckinStore>((set, get) => ({
  ...initialState,

  checkIn: async () => {
    set({ isLoading: true, error: null });
    try {
      await checkinService.checkIn();
      // Refresh status after check-in
      await get().fetchStatus();
      set({ isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '체크인에 실패했습니다.',
      });
      throw error;
    }
  },

  fetchStatus: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await checkinService.getStatus();
      set({
        status: mapStatusResponse(response),
        isLoading: false,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '상태를 불러오는데 실패했습니다.',
      });
      // Don't throw - status fetch failure shouldn't break the app
      console.error('Failed to fetch check-in status:', error);
    }
  },

  fetchHistory: async (page = 1, limit = 20) => {
    set({ isLoading: true, error: null });
    try {
      const response = await checkinService.getHistory(page, limit);
      set({
        history: response.checkins,
        isLoading: false,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '체크인 기록을 불러오는데 실패했습니다.',
      });
    }
  },

  updateSettings: async (cycleDays: number, gracePeriodHours: number) => {
    set({ isUpdatingSettings: true, error: null });
    try {
      await checkinService.updateSettings({
        checkin_cycle_days: cycleDays,
        grace_period_hours: gracePeriodHours,
      });
      // Refresh status after settings update
      await get().fetchStatus();
      set({ isUpdatingSettings: false });
    } catch (error) {
      set({
        isUpdatingSettings: false,
        error: error instanceof Error ? error.message : '설정 업데이트에 실패했습니다.',
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

export default useCheckinStore;
