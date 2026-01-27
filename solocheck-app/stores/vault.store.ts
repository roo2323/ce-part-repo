import { create } from 'zustand';
import { vaultService } from '@/services/vault.service';
import type { VaultItem, CreateVaultRequest, UpdateVaultRequest } from '@/types';

interface VaultState {
  items: VaultItem[];
  currentItem: VaultItem | null;
  isLoading: boolean;
  error: string | null;
}

interface VaultActions {
  fetchVaultItems: () => Promise<void>;
  fetchVaultItem: (vaultId: string) => Promise<VaultItem>;
  createVaultItem: (data: CreateVaultRequest) => Promise<VaultItem>;
  updateVaultItem: (vaultId: string, data: UpdateVaultRequest) => Promise<VaultItem>;
  deleteVaultItem: (vaultId: string) => Promise<void>;
  clearCurrentItem: () => void;
  clearError: () => void;
  reset: () => void;
}

type VaultStore = VaultState & VaultActions;

const initialState: VaultState = {
  items: [],
  currentItem: null,
  isLoading: false,
  error: null,
};

export const useVaultStore = create<VaultStore>((set, get) => ({
  ...initialState,

  fetchVaultItems: async () => {
    set({ isLoading: true, error: null });
    try {
      const result = await vaultService.getVaultItems();
      set({ items: result.items, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '정보 금고 목록을 불러오는데 실패했습니다.',
      });
      throw error;
    }
  },

  fetchVaultItem: async (vaultId) => {
    set({ isLoading: true, error: null });
    try {
      const item = await vaultService.getVaultItem(vaultId);
      set({ currentItem: item, isLoading: false });
      return item;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '정보를 불러오는데 실패했습니다.',
      });
      throw error;
    }
  },

  createVaultItem: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const item = await vaultService.createVaultItem(data);
      set((state) => ({
        items: [...state.items, item],
        isLoading: false,
      }));
      return item;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '정보 저장에 실패했습니다.',
      });
      throw error;
    }
  },

  updateVaultItem: async (vaultId, data) => {
    set({ isLoading: true, error: null });
    try {
      const updatedItem = await vaultService.updateVaultItem(vaultId, data);
      set((state) => ({
        items: state.items.map((item) => (item.id === vaultId ? updatedItem : item)),
        currentItem: state.currentItem?.id === vaultId ? updatedItem : state.currentItem,
        isLoading: false,
      }));
      return updatedItem;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '정보 수정에 실패했습니다.',
      });
      throw error;
    }
  },

  deleteVaultItem: async (vaultId) => {
    set({ isLoading: true, error: null });
    try {
      await vaultService.deleteVaultItem(vaultId);
      set((state) => ({
        items: state.items.filter((item) => item.id !== vaultId),
        currentItem: state.currentItem?.id === vaultId ? null : state.currentItem,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '정보 삭제에 실패했습니다.',
      });
      throw error;
    }
  },

  clearCurrentItem: () => {
    set({ currentItem: null });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));

export default useVaultStore;
