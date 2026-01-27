import { create } from 'zustand';
import { sosService } from '@/services/sos.service';
import type { SOSEvent } from '@/types';

interface SOSState {
  activeEvent: SOSEvent | null;
  isTriggering: boolean;
  isCancelling: boolean;
  countdownSeconds: number;
  error: string | null;
}

interface SOSActions {
  trigger: (location?: { lat: number; lng: number }) => Promise<SOSEvent>;
  cancel: () => Promise<void>;
  checkStatus: () => Promise<void>;
  decrementCountdown: () => void;
  clearError: () => void;
  reset: () => void;
}

type SOSStore = SOSState & SOSActions;

const initialState: SOSState = {
  activeEvent: null,
  isTriggering: false,
  isCancelling: false,
  countdownSeconds: 0,
  error: null,
};

export const useSOSStore = create<SOSStore>((set, get) => ({
  ...initialState,

  trigger: async (location) => {
    set({ isTriggering: true, error: null });
    try {
      const result = await sosService.trigger(location);
      set({
        activeEvent: result.event,
        countdownSeconds: result.countdown_seconds,
        isTriggering: false,
      });
      return result.event;
    } catch (error) {
      set({
        isTriggering: false,
        error: error instanceof Error ? error.message : 'SOS 발송에 실패했습니다.',
      });
      throw error;
    }
  },

  cancel: async () => {
    const { activeEvent } = get();
    if (!activeEvent) return;

    set({ isCancelling: true, error: null });
    try {
      await sosService.cancel(activeEvent.id);
      set({
        activeEvent: null,
        countdownSeconds: 0,
        isCancelling: false,
      });
    } catch (error) {
      set({
        isCancelling: false,
        error: error instanceof Error ? error.message : 'SOS 취소에 실패했습니다.',
      });
      throw error;
    }
  },

  checkStatus: async () => {
    try {
      const status = await sosService.getStatus();
      set({
        activeEvent: status.activeEvent || null,
      });
    } catch (error) {
      console.error('Failed to check SOS status:', error);
    }
  },

  decrementCountdown: () => {
    const { countdownSeconds, activeEvent } = get();
    if (countdownSeconds > 0) {
      set({ countdownSeconds: countdownSeconds - 1 });
    } else if (activeEvent && activeEvent.status === 'triggered') {
      // Countdown finished, update status
      set({
        activeEvent: { ...activeEvent, status: 'sent' },
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));

export default useSOSStore;
