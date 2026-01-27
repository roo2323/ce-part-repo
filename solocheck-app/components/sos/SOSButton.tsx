import { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Vibration,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as Location from 'expo-location';
import { useSOSStore } from '@/stores/sos.store';

interface SOSButtonProps {
  onTriggered?: () => void;
}

const LONG_PRESS_DURATION = 3000; // 3 seconds to trigger

export default function SOSButton({ onTriggered }: SOSButtonProps) {
  const [isPressing, setIsPressing] = useState(false);
  const progress = useRef(new Animated.Value(0)).current;
  const pressTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { trigger, isTriggering } = useSOSStore();

  const handlePressIn = useCallback(() => {
    setIsPressing(true);

    // Start haptic feedback
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);

    // Start progress animation
    Animated.timing(progress, {
      toValue: 1,
      duration: LONG_PRESS_DURATION,
      useNativeDriver: false,
    }).start();

    // Start timer for trigger
    pressTimer.current = setTimeout(async () => {
      // Strong haptic on trigger
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      Vibration.vibrate([0, 100, 100, 100]);

      // Try to get location
      let location: { lat: number; lng: number } | undefined;
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const currentLocation = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Balanced,
          });
          location = {
            lat: currentLocation.coords.latitude,
            lng: currentLocation.coords.longitude,
          };
        }
      } catch (error) {
        console.log('Could not get location:', error);
      }

      // Trigger SOS
      try {
        await trigger(location);
        onTriggered?.();
      } catch (error) {
        Alert.alert(
          '오류',
          error instanceof Error ? error.message : 'SOS 발송에 실패했습니다.'
        );
      }

      handlePressOut();
    }, LONG_PRESS_DURATION);
  }, [trigger, onTriggered, progress]);

  const handlePressOut = useCallback(() => {
    setIsPressing(false);

    // Clear timer
    if (pressTimer.current) {
      clearTimeout(pressTimer.current);
      pressTimer.current = null;
    }

    // Reset animation
    Animated.timing(progress, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  const progressWidth = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.button, isPressing && styles.buttonPressing]}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
        disabled={isTriggering}
      >
        <Animated.View
          style={[
            styles.progressOverlay,
            {
              width: progressWidth,
            },
          ]}
        />
        <View style={styles.content}>
          <Ionicons
            name="warning"
            size={28}
            color={isPressing ? '#ffffff' : '#ff3b30'}
          />
          <Text style={[styles.text, isPressing && styles.textPressing]}>
            {isPressing ? '계속 누르세요...' : 'SOS'}
          </Text>
        </View>
      </TouchableOpacity>
      <Text style={styles.hint}>
        3초간 길게 누르면 비상연락처에 알림이 전송됩니다
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  button: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#fff5f5',
    borderWidth: 4,
    borderColor: '#ff3b30',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    shadowColor: '#ff3b30',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  buttonPressing: {
    borderColor: '#cc2f27',
  },
  progressOverlay: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    backgroundColor: '#ff3b30',
  },
  content: {
    alignItems: 'center',
    zIndex: 1,
  },
  text: {
    fontSize: 18,
    fontWeight: '700',
    color: '#ff3b30',
    marginTop: 4,
  },
  textPressing: {
    color: '#ffffff',
    fontSize: 14,
  },
  hint: {
    marginTop: 12,
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    maxWidth: 200,
  },
});
