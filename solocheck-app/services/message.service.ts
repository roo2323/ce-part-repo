import { api, getErrorMessage } from './api';

/**
 * Personal message response from the API
 */
export interface MessageResponse {
  id: string | null;
  content: string | null;
  is_enabled: boolean;
  character_count: number;
  max_characters: number;
  updated_at: string | null;
}

/**
 * Request to update the personal message
 */
export interface MessageUpdateRequest {
  content: string;
  is_enabled: boolean;
}

/**
 * Response from message deletion
 */
export interface MessageDeleteResponse {
  message: string;
  deleted: boolean;
}

export const messageService = {
  /**
   * Get the current user's personal message
   */
  async getMessage(): Promise<MessageResponse> {
    try {
      const response = await api.get<MessageResponse>('/message');
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Save or update the personal message
   */
  async saveMessage(data: MessageUpdateRequest): Promise<MessageResponse> {
    try {
      const response = await api.put<MessageResponse>('/message', data);
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Delete the personal message
   */
  async deleteMessage(): Promise<MessageDeleteResponse> {
    try {
      const response = await api.delete<MessageDeleteResponse>('/message');
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default messageService;
