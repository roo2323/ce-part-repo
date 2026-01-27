import { useEffect, useCallback, useState } from 'react';
import * as Linking from 'expo-linking';
import * as Haptics from 'expo-haptics';
import { Alert } from 'react-native';
import { parseDeepLink, isAutoCheckInLink, deeplinkService } from '@/services/deeplink.service';
import { useCheckinStore } from '@/stores/checkin.store';

interface DeepLinkState {
  isProcessing: boolean;
  lastProcessedUrl: string | null;
}

export const useDeepLink = () => {
  const [state, setState] = useState<DeepLinkState>({
    isProcessing: false,
    lastProcessedUrl: null,
  });
  const { fetchStatus } = useCheckinStore();

  const handleDeepLink = useCallback(async (url: string) => {
    // Prevent processing the same URL twice
    if (state.isProcessing || url === state.lastProcessedUrl) {
      return;
    }

    const params = parseDeepLink(url);
    if (!params) {
      return;
    }

    // Check if this is an auto check-in link
    if (isAutoCheckInLink(params)) {
      setState({ isProcessing: true, lastProcessedUrl: url });

      try {
        const result = await deeplinkService.quickCheckIn(params.token!);

        if (result.success) {
          // Haptic feedback for successful check-in
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

          // Show success toast/alert
          Alert.alert(
            '체크인 완료',
            result.message,
            [{ text: '확인', style: 'default' }],
            { cancelable: true }
          );

          // Refresh check-in status
          await fetchStatus();
        } else {
          // Haptic feedback for failure
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

          Alert.alert(
            '체크인 실패',
            result.message,
            [{ text: '확인', style: 'default' }],
            { cancelable: true }
          );
        }
      } catch (error) {
        // Haptic feedback for error
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

        Alert.alert(
          '오류',
          error instanceof Error ? error.message : '체크인 처리 중 오류가 발생했습니다.',
          [{ text: '확인', style: 'default' }],
          { cancelable: true }
        );
      } finally {
        setState((prev) => ({ ...prev, isProcessing: false }));
      }
    }
  }, [state.isProcessing, state.lastProcessedUrl, fetchStatus]);

  useEffect(() => {
    // Handle initial URL (app opened via deep link)
    const getInitialURL = async () => {
      const initialUrl = await Linking.getInitialURL();
      if (initialUrl) {
        handleDeepLink(initialUrl);
      }
    };

    getInitialURL();

    // Listen for incoming deep links while app is running
    const subscription = Linking.addEventListener('url', (event) => {
      handleDeepLink(event.url);
    });

    return () => {
      subscription.remove();
    };
  }, [handleDeepLink]);

  return {
    isProcessing: state.isProcessing,
  };
};

export default useDeepLink;
