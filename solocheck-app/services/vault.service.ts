import { api, getErrorMessage } from './api';
import type { VaultItem, CreateVaultRequest, UpdateVaultRequest, VaultListResponse } from '@/types';

// API Response types (snake_case from backend)
interface VaultApiResponse {
  id: string;
  user_id: string;
  category: string;
  title: string;
  include_in_alert: boolean;
  created_at: string;
  updated_at: string;
}

interface VaultDetailApiResponse extends VaultApiResponse {
  content: string;
}

interface VaultListApiResponse {
  items: VaultApiResponse[];
  total: number;
}

// Transform API response to frontend format
const transformVaultItem = (data: VaultApiResponse): VaultItem => ({
  id: data.id,
  userId: data.user_id,
  category: data.category as VaultItem['category'],
  title: data.title,
  includeInAlert: data.include_in_alert,
  createdAt: data.created_at,
  updatedAt: data.updated_at,
});

const transformVaultDetail = (data: VaultDetailApiResponse): VaultItem => ({
  ...transformVaultItem(data),
  content: data.content,
});

export const vaultService = {
  /**
   * Get all vault items for the current user
   */
  async getVaultItems(): Promise<VaultListResponse> {
    try {
      const response = await api.get<VaultListApiResponse>('/vault');
      return {
        items: response.data.items.map(transformVaultItem),
        total: response.data.total,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get a specific vault item by ID (with decrypted content)
   */
  async getVaultItem(vaultId: string): Promise<VaultItem> {
    try {
      const response = await api.get<VaultDetailApiResponse>(`/vault/${vaultId}`);
      return transformVaultDetail(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Create a new vault item
   */
  async createVaultItem(data: CreateVaultRequest): Promise<VaultItem> {
    try {
      const response = await api.post<VaultApiResponse>('/vault', data);
      return transformVaultItem(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update a vault item
   */
  async updateVaultItem(vaultId: string, data: UpdateVaultRequest): Promise<VaultItem> {
    try {
      const response = await api.put<VaultApiResponse>(`/vault/${vaultId}`, data);
      return transformVaultItem(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Delete a vault item
   */
  async deleteVaultItem(vaultId: string): Promise<void> {
    try {
      await api.delete(`/vault/${vaultId}`);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default vaultService;
