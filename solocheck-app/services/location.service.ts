import { api, getErrorMessage } from './api';
import type {
  LocationConsent,
  LocationConsentResponse,
  LocationSharingLog,
  LocationSharingHistoryResponse,
} from '@/types';

// API Response types (snake_case from backend)
interface LocationSharingLogApiResponse {
  id: string;
  user_id: string;
  event_type: string;
  location_lat: number | null;
  location_lng: number | null;
  recipient_ids: string[] | null;
  shared_at: string;
  created_at: string;
}

interface LocationSharingHistoryApiResponse {
  logs: LocationSharingLogApiResponse[];
  total: number;
}

// Transform API response to frontend format
const transformLog = (data: LocationSharingLogApiResponse): LocationSharingLog => ({
  id: data.id,
  userId: data.user_id,
  eventType: data.event_type as 'sos' | 'missed_checkin',
  locationLat: data.location_lat,
  locationLng: data.location_lng,
  recipientIds: data.recipient_ids,
  sharedAt: data.shared_at,
  createdAt: data.created_at,
});

export const locationService = {
  /**
   * Get current location consent status
   */
  async getConsent(): Promise<LocationConsent> {
    try {
      const response = await api.get<LocationConsentResponse>('/location/consent');
      return {
        locationConsent: response.data.location_consent,
        locationConsentAt: response.data.location_consent_at,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update location consent
   */
  async updateConsent(consent: boolean): Promise<LocationConsent> {
    try {
      const response = await api.post<LocationConsentResponse>('/location/consent', {
        consent,
      });
      return {
        locationConsent: response.data.location_consent,
        locationConsentAt: response.data.location_consent_at,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get location sharing history
   */
  async getHistory(limit: number = 50): Promise<LocationSharingHistoryResponse> {
    try {
      const response = await api.get<LocationSharingHistoryApiResponse>(
        `/location/history?limit=${limit}`
      );
      return {
        logs: response.data.logs.map(transformLog),
        total: response.data.total,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default locationService;
