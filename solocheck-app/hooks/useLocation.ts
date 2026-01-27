import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';

interface LocationData {
  lat: number;
  lng: number;
}

interface UseLocationResult {
  location: LocationData | null;
  isLoading: boolean;
  error: string | null;
  hasPermission: boolean | null;
  requestPermission: () => Promise<boolean>;
  getCurrentLocation: () => Promise<LocationData | null>;
}

export function useLocation(): UseLocationResult {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  useEffect(() => {
    checkPermission();
  }, []);

  const checkPermission = useCallback(async () => {
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      setHasPermission(status === 'granted');
    } catch (err) {
      setError('위치 권한 확인에 실패했습니다.');
      setHasPermission(false);
    }
  }, []);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      const granted = status === 'granted';
      setHasPermission(granted);
      return granted;
    } catch (err) {
      setError('위치 권한 요청에 실패했습니다.');
      setHasPermission(false);
      return false;
    }
  }, []);

  const getCurrentLocation = useCallback(async (): Promise<LocationData | null> => {
    setIsLoading(true);
    setError(null);

    try {
      // Check permission first
      if (!hasPermission) {
        const granted = await requestPermission();
        if (!granted) {
          setError('위치 권한이 필요합니다.');
          setIsLoading(false);
          return null;
        }
      }

      // Get current location
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      const locationData: LocationData = {
        lat: currentLocation.coords.latitude,
        lng: currentLocation.coords.longitude,
      };

      setLocation(locationData);
      setIsLoading(false);
      return locationData;
    } catch (err) {
      setError('현재 위치를 가져오는데 실패했습니다.');
      setIsLoading(false);
      return null;
    }
  }, [hasPermission, requestPermission]);

  return {
    location,
    isLoading,
    error,
    hasPermission,
    requestPermission,
    getCurrentLocation,
  };
}

export default useLocation;
