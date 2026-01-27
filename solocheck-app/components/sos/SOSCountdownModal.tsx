import { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  Animated,
  Vibration,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSOSStore } from '@/stores/sos.store';

interface SOSCountdownModalProps {
  visible: boolean;
  onDismiss: () => void;
}

export default function SOSCountdownModal({
  visible,
  onDismiss,
}: SOSCountdownModalProps) {
  const { activeEvent, countdownSeconds, decrementCountdown, cancel, isCancelling } =
    useSOSStore();
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Countdown timer
  useEffect(() => {
    if (!visible || countdownSeconds <= 0) return;

    const interval = setInterval(() => {
      decrementCountdown();
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }, 1000);

    return () => clearInterval(interval);
  }, [visible, countdownSeconds, decrementCountdown]);

  // Check if countdown finished
  useEffect(() => {
    if (visible && countdownSeconds === 0 && activeEvent?.status === 'sent') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Vibration.vibrate([0, 200, 100, 200]);
    }
  }, [visible, countdownSeconds, activeEvent?.status]);

  // Pulse animation
  useEffect(() => {
    if (!visible) return;

    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
      ])
    );

    pulse.start();
    return () => pulse.stop();
  }, [visible, pulseAnim]);

  const handleCancel = async () => {
    try {
      await cancel();
      onDismiss();
    } catch (error) {
      // Error handled in store
    }
  };

  const isSent = activeEvent?.status === 'sent' || countdownSeconds === 0;

  return (
    <Modal
      visible={visible}
      animationType="fade"
      transparent
      onRequestClose={handleCancel}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          <Animated.View
            style={[
              styles.iconContainer,
              isSent ? styles.iconContainerSent : styles.iconContainerWarning,
              { transform: [{ scale: pulseAnim }] },
            ]}
          >
            <Ionicons
              name={isSent ? 'checkmark-circle' : 'warning'}
              size={60}
              color="#ffffff"
            />
          </Animated.View>

          {isSent ? (
            <>
              <Text style={styles.title}>알림 발송 완료</Text>
              <Text style={styles.message}>
                비상연락처에 SOS 알림이 발송되었습니다.
              </Text>
              <TouchableOpacity style={styles.dismissButton} onPress={onDismiss}>
                <Text style={styles.dismissButtonText}>확인</Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              <Text style={styles.title}>SOS 발동됨</Text>
              <Text style={styles.countdown}>{countdownSeconds}</Text>
              <Text style={styles.message}>
                {countdownSeconds}초 후 비상연락처에 알림이 발송됩니다.
              </Text>

              <TouchableOpacity
                style={[styles.cancelButton, isCancelling && styles.cancelButtonDisabled]}
                onPress={handleCancel}
                disabled={isCancelling}
              >
                <Ionicons name="close-circle" size={24} color="#ffffff" />
                <Text style={styles.cancelButtonText}>
                  {isCancelling ? '취소 중...' : '취소하기'}
                </Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  container: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 32,
    width: '100%',
    maxWidth: 320,
    alignItems: 'center',
  },
  iconContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  iconContainerWarning: {
    backgroundColor: '#ff3b30',
  },
  iconContainerSent: {
    backgroundColor: '#34c759',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  countdown: {
    fontSize: 72,
    fontWeight: '700',
    color: '#ff3b30',
    marginVertical: 16,
  },
  message: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  cancelButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#666',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
    gap: 8,
  },
  cancelButtonDisabled: {
    backgroundColor: '#ccc',
  },
  cancelButtonText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#ffffff',
  },
  dismissButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 48,
    borderRadius: 12,
  },
  dismissButtonText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#ffffff',
  },
});
