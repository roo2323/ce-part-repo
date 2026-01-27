import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useReminderStore } from '@/stores/reminder.store';
import type { UpdateReminderSettingsRequest } from '@/types';

// Predefined hour options for reminder timing
const HOUR_OPTIONS = [72, 48, 24, 12, 6, 3];

export default function ReminderSettingsScreen() {
  const { settings, isLoading, isUpdating, error, fetchSettings, updateSettings, clearQuietHours } =
    useReminderStore();

  // Local state for form
  const [selectedHours, setSelectedHours] = useState<number[]>([48, 24, 12]);
  const [pushEnabled, setPushEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [customMessage, setCustomMessage] = useState('');
  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false);
  const [quietStart, setQuietStart] = useState('22:00');
  const [quietEnd, setQuietEnd] = useState('08:00');

  // Load settings on mount
  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Sync local state with loaded settings
  useEffect(() => {
    if (settings) {
      setSelectedHours(settings.reminderHoursBefore || [48, 24, 12]);
      setPushEnabled(settings.pushEnabled);
      setEmailEnabled(settings.emailEnabled);
      setCustomMessage(settings.customMessage || '');
      setQuietHoursEnabled(!!settings.quietHoursStart && !!settings.quietHoursEnd);
      if (settings.quietHoursStart) setQuietStart(settings.quietHoursStart);
      if (settings.quietHoursEnd) setQuietEnd(settings.quietHoursEnd);
    }
  }, [settings]);

  // Toggle hour selection
  const toggleHour = (hour: number) => {
    setSelectedHours((prev) => {
      if (prev.includes(hour)) {
        // Don't allow removing all hours
        if (prev.length <= 1) return prev;
        return prev.filter((h) => h !== hour);
      } else {
        return [...prev, hour].sort((a, b) => b - a);
      }
    });
  };

  // Save settings
  const handleSave = async () => {
    try {
      const data: UpdateReminderSettingsRequest = {
        reminder_hours_before: selectedHours,
        push_enabled: pushEnabled,
        email_enabled: emailEnabled,
        custom_message: customMessage.trim() || null,
      };

      if (quietHoursEnabled) {
        data.quiet_hours_start = quietStart;
        data.quiet_hours_end = quietEnd;
      } else {
        data.quiet_hours_start = null;
        data.quiet_hours_end = null;
      }

      await updateSettings(data);
      Alert.alert('저장 완료', '리마인더 설정이 저장되었습니다.');
    } catch (err) {
      Alert.alert('오류', '설정 저장에 실패했습니다.');
    }
  };

  // Format hour display
  const formatHour = (hours: number): string => {
    if (hours >= 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      if (remainingHours === 0) {
        return `${days}일 전`;
      }
      return `${days}일 ${remainingHours}시간 전`;
    }
    return `${hours}시간 전`;
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>설정을 불러오는 중...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Notification Channels */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>알림 채널</Text>
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <View style={styles.iconContainer}>
                  <Ionicons name="phone-portrait-outline" size={20} color="#007AFF" />
                </View>
                <View>
                  <Text style={styles.settingLabel}>푸시 알림</Text>
                  <Text style={styles.settingDescription}>앱 푸시 알림으로 리마인더 받기</Text>
                </View>
              </View>
              <Switch
                value={pushEnabled}
                onValueChange={setPushEnabled}
                trackColor={{ false: '#e0e0e0', true: '#007AFF' }}
                thumbColor="#ffffff"
              />
            </View>
            <View style={styles.divider} />
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <View style={styles.iconContainer}>
                  <Ionicons name="mail-outline" size={20} color="#007AFF" />
                </View>
                <View>
                  <Text style={styles.settingLabel}>이메일 알림</Text>
                  <Text style={styles.settingDescription}>이메일로 리마인더 받기</Text>
                </View>
              </View>
              <Switch
                value={emailEnabled}
                onValueChange={setEmailEnabled}
                trackColor={{ false: '#e0e0e0', true: '#007AFF' }}
                thumbColor="#ffffff"
              />
            </View>
          </View>
        </View>

        {/* Reminder Timing */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>리마인더 타이밍</Text>
          <Text style={styles.sectionDescription}>체크인 마감 전 언제 리마인더를 받을지 선택하세요</Text>
          <View style={styles.card}>
            <View style={styles.hoursGrid}>
              {HOUR_OPTIONS.map((hour) => (
                <TouchableOpacity
                  key={hour}
                  style={[styles.hourChip, selectedHours.includes(hour) && styles.hourChipSelected]}
                  onPress={() => toggleHour(hour)}
                >
                  <Text
                    style={[styles.hourChipText, selectedHours.includes(hour) && styles.hourChipTextSelected]}
                  >
                    {formatHour(hour)}
                  </Text>
                  {selectedHours.includes(hour) && (
                    <Ionicons name="checkmark-circle" size={16} color="#007AFF" style={styles.checkIcon} />
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* Quiet Hours */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>방해금지 시간</Text>
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <View style={styles.iconContainer}>
                  <Ionicons name="moon-outline" size={20} color="#007AFF" />
                </View>
                <View>
                  <Text style={styles.settingLabel}>방해금지 모드</Text>
                  <Text style={styles.settingDescription}>설정한 시간에는 알림을 보내지 않습니다</Text>
                </View>
              </View>
              <Switch
                value={quietHoursEnabled}
                onValueChange={setQuietHoursEnabled}
                trackColor={{ false: '#e0e0e0', true: '#007AFF' }}
                thumbColor="#ffffff"
              />
            </View>
            {quietHoursEnabled && (
              <>
                <View style={styles.divider} />
                <View style={styles.timeInputRow}>
                  <View style={styles.timeInputGroup}>
                    <Text style={styles.timeLabel}>시작</Text>
                    <TextInput
                      style={styles.timeInput}
                      value={quietStart}
                      onChangeText={setQuietStart}
                      placeholder="22:00"
                      keyboardType="numbers-and-punctuation"
                    />
                  </View>
                  <Ionicons name="arrow-forward" size={20} color="#ccc" />
                  <View style={styles.timeInputGroup}>
                    <Text style={styles.timeLabel}>종료</Text>
                    <TextInput
                      style={styles.timeInput}
                      value={quietEnd}
                      onChangeText={setQuietEnd}
                      placeholder="08:00"
                      keyboardType="numbers-and-punctuation"
                    />
                  </View>
                </View>
              </>
            )}
          </View>
        </View>

        {/* Custom Message */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>커스텀 메시지</Text>
          <Text style={styles.sectionDescription}>리마인더에 표시될 나만의 메시지 (최대 100자)</Text>
          <View style={styles.card}>
            <TextInput
              style={styles.messageInput}
              value={customMessage}
              onChangeText={(text) => setCustomMessage(text.slice(0, 100))}
              placeholder="예: 오늘도 체크인 잊지 마세요!"
              multiline
              maxLength={100}
            />
            <Text style={styles.charCount}>{customMessage.length}/100</Text>
          </View>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, isUpdating && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isUpdating}
        >
          {isUpdating ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.saveButtonText}>저장하기</Text>
          )}
        </TouchableOpacity>

        {error && <Text style={styles.errorText}>{error}</Text>}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  sectionDescription: {
    fontSize: 13,
    color: '#999',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#e8f4ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  settingDescription: {
    fontSize: 13,
    color: '#999',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginVertical: 12,
  },
  hoursGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  hourChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  hourChipSelected: {
    backgroundColor: '#e8f4ff',
    borderColor: '#007AFF',
  },
  hourChipText: {
    fontSize: 14,
    color: '#666',
  },
  hourChipTextSelected: {
    color: '#007AFF',
    fontWeight: '500',
  },
  checkIcon: {
    marginLeft: 4,
  },
  timeInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingTop: 8,
  },
  timeInputGroup: {
    alignItems: 'center',
  },
  timeLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  timeInput: {
    fontSize: 18,
    fontWeight: '500',
    color: '#333',
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    minWidth: 100,
    textAlign: 'center',
  },
  messageInput: {
    fontSize: 16,
    color: '#333',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
    marginTop: 8,
  },
  saveButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  saveButtonDisabled: {
    backgroundColor: '#ccc',
  },
  saveButtonText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#ffffff',
  },
  errorText: {
    fontSize: 14,
    color: '#ff3b30',
    textAlign: 'center',
    marginTop: 12,
  },
});
