import { api, getErrorMessage } from './api';
import type { QuickCheckInRequest, QuickCheckInResponse, DeepLinkParams } from '@/types';

/**
 * Parse deep link URL to extract parameters
 * @param url - The deep link URL (e.g., solocheck://checkin?auto=true&token=xxx)
 * @returns Parsed parameters or null if invalid
 */
export const parseDeepLink = (url: string): DeepLinkParams | null => {
  try {
    // Handle solocheck:// scheme
    if (!url.startsWith('solocheck://')) {
      return null;
    }

    // Parse the URL
    const urlWithoutScheme = url.replace('solocheck://', 'https://solocheck.app/');
    const parsedUrl = new URL(urlWithoutScheme);
    const params: DeepLinkParams = {};

    // Extract parameters
    if (parsedUrl.searchParams.has('auto')) {
      params.auto = parsedUrl.searchParams.get('auto') || undefined;
    }
    if (parsedUrl.searchParams.has('token')) {
      params.token = parsedUrl.searchParams.get('token') || undefined;
    }

    return params;
  } catch (error) {
    console.error('Failed to parse deep link:', error);
    return null;
  }
};

/**
 * Check if the deep link is for auto check-in
 */
export const isAutoCheckInLink = (params: DeepLinkParams): boolean => {
  return params.auto === 'true' && !!params.token;
};

/**
 * Service for deep link related API calls
 */
export const deeplinkService = {
  /**
   * Perform quick check-in using session token from push notification
   */
  async quickCheckIn(token: string, deviceType: 'push' | 'widget' = 'push'): Promise<QuickCheckInResponse> {
    try {
      const request: QuickCheckInRequest = {
        token,
        device_type: deviceType,
      };
      const response = await api.post<QuickCheckInResponse>('/checkin/quick', request);
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default deeplinkService;
