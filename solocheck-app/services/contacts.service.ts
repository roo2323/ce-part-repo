import { api, getErrorMessage } from './api';
import type { EmergencyContact, CreateContactRequest, UpdateContactRequest } from '@/types';

// Backend API types
interface BackendContactCreateRequest {
  name: string;
  contact_type: 'email' | 'sms';
  contact_value: string;
  priority?: number;
}

interface BackendContactResponse {
  id: string;
  name: string;
  contact_type: string;
  contact_value: string;
  priority: number;
  is_verified: boolean;
  created_at: string;
}

interface BackendContactListResponse {
  data: BackendContactResponse[];
  max_contacts: number;
  current_count: number;
}

// Transform backend response to frontend format
const transformContact = (contact: BackendContactResponse): EmergencyContact => ({
  id: contact.id,
  userId: '',
  name: contact.name,
  phone: contact.contact_type === 'sms' ? contact.contact_value : '',
  email: contact.contact_type === 'email' ? contact.contact_value : undefined,
  isVerified: contact.is_verified,
  createdAt: contact.created_at,
  updatedAt: contact.created_at,
});

export const contactsService = {
  /**
   * Get all emergency contacts
   */
  async getContacts(): Promise<EmergencyContact[]> {
    try {
      const response = await api.get<BackendContactListResponse>('/contacts');
      return response.data.data.map(transformContact);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get a single emergency contact
   */
  async getContact(id: string): Promise<EmergencyContact> {
    try {
      const response = await api.get<BackendContactResponse>(`/contacts/${id}`);
      return transformContact(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Create a new emergency contact
   */
  async createContact(data: CreateContactRequest): Promise<EmergencyContact> {
    try {
      // Transform frontend data to backend format
      // Prefer phone (SMS) if provided, otherwise use email
      const backendData: BackendContactCreateRequest = {
        name: data.name,
        contact_type: data.phone ? 'sms' : 'email',
        contact_value: data.phone || data.email || '',
      };

      const response = await api.post<BackendContactResponse>('/contacts', backendData);
      return transformContact(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update an emergency contact
   */
  async updateContact(id: string, data: UpdateContactRequest): Promise<EmergencyContact> {
    try {
      // Backend only allows updating name and priority
      const backendData: { name?: string; priority?: number } = {};
      if (data.name) backendData.name = data.name;

      const response = await api.put<BackendContactResponse>(`/contacts/${id}`, backendData);
      return transformContact(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Delete an emergency contact
   */
  async deleteContact(id: string): Promise<void> {
    try {
      await api.delete(`/contacts/${id}`);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Send test notification to an emergency contact
   */
  async sendTestNotification(id: string): Promise<void> {
    try {
      await api.post(`/contacts/${id}/test-notification`);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default contactsService;
