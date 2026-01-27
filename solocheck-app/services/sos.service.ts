import { api, getErrorMessage } from './api';
import type { SOSEvent, SOSTriggerRequest, SOSTriggerResponse, SOSCancelResponse } from '@/types';

// API Response types (snake_case from backend)
interface SOSEventApiResponse {
  id: string;
  user_id: string;
  triggered_at: string;
  cancelled_at: string | null;
  sent_at: string | null;
  location_lat: number | null;
  location_lng: number | null;
  status: string;
  created_at: string;
}

interface SOSTriggerApiResponse {
  message: string;
  event: SOSEventApiResponse;
  countdown_seconds: number;
}

interface SOSCancelApiResponse {
  message: string;
  event: SOSEventApiResponse;
}

interface SOSStatusApiResponse {
  has_active_sos: boolean;
  active_event: SOSEventApiResponse | null;
}

// Transform API response to frontend format
const transformEvent = (data: SOSEventApiResponse): SOSEvent => ({
  id: data.id,
  userId: data.user_id,
  triggeredAt: data.triggered_at,
  cancelledAt: data.cancelled_at || undefined,
  sentAt: data.sent_at || undefined,
  locationLat: data.location_lat || undefined,
  locationLng: data.location_lng || undefined,
  status: data.status as SOSEvent['status'],
  createdAt: data.created_at,
});

export const sosService = {
  /**
   * Trigger an SOS emergency alert
   */
  async trigger(location?: { lat: number; lng: number }): Promise<SOSTriggerResponse> {
    try {
      const request: SOSTriggerRequest = {};
      if (location) {
        request.location_lat = location.lat;
        request.location_lng = location.lng;
      }

      const response = await api.post<SOSTriggerApiResponse>('/sos/trigger', request);
      return {
        message: response.data.message,
        event: transformEvent(response.data.event),
        countdown_seconds: response.data.countdown_seconds,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Cancel an active SOS alert
   */
  async cancel(sosId: string): Promise<SOSCancelResponse> {
    try {
      const response = await api.post<SOSCancelApiResponse>(`/sos/${sosId}/cancel`);
      return {
        message: response.data.message,
        event: transformEvent(response.data.event),
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get current SOS status
   */
  async getStatus(): Promise<{ hasActiveSOS: boolean; activeEvent?: SOSEvent }> {
    try {
      const response = await api.get<SOSStatusApiResponse>('/sos/status');
      return {
        hasActiveSOS: response.data.has_active_sos,
        activeEvent: response.data.active_event
          ? transformEvent(response.data.active_event)
          : undefined,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default sosService;
