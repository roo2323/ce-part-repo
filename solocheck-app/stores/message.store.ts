import { create } from 'zustand';
import { messageService, MessageResponse } from '@/services/message.service';

interface MessageState {
  message: MessageResponse | null;
  isLoading: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  error: string | null;
}

interface MessageActions {
  fetchMessage: () => Promise<void>;
  saveMessage: (content: string, isEnabled: boolean) => Promise<void>;
  deleteMessage: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

type MessageStore = MessageState & MessageActions;

const initialState: MessageState = {
  message: null,
  isLoading: false,
  isSaving: false,
  isDeleting: false,
  error: null,
};

export const useMessageStore = create<MessageStore>((set) => ({
  ...initialState,

  fetchMessage: async () => {
    set({ isLoading: true, error: null });
    try {
      const message = await messageService.getMessage();
      set({ message, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '메시지를 불러오는데 실패했습니다.',
      });
    }
  },

  saveMessage: async (content: string, isEnabled: boolean) => {
    set({ isSaving: true, error: null });
    try {
      const message = await messageService.saveMessage({ content, is_enabled: isEnabled });
      set({ message, isSaving: false });
    } catch (error) {
      set({
        isSaving: false,
        error: error instanceof Error ? error.message : '메시지 저장에 실패했습니다.',
      });
      throw error;
    }
  },

  deleteMessage: async () => {
    set({ isDeleting: true, error: null });
    try {
      await messageService.deleteMessage();
      set({
        message: {
          id: null,
          content: null,
          is_enabled: false,
          character_count: 0,
          max_characters: 2000,
          updated_at: null,
        },
        isDeleting: false,
      });
    } catch (error) {
      set({
        isDeleting: false,
        error: error instanceof Error ? error.message : '메시지 삭제에 실패했습니다.',
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));

export default useMessageStore;
