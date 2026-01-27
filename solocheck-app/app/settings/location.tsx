import { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Stack } from 'expo-router';
import { locationService } from '@/services/location.service';
import { useLocation } from '@/hooks/useLocation';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '@/constants';
import type { LocationConsent, LocationSharingLog } from '@/types';

export default function LocationSettingsScreen() {
  const { hasPermission, requestPermission } = useLocation();
  const [consent, setConsent] = useState<LocationConsent | null>(null);
  const [history, setHistory] = useState<LocationSharingLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [consentData, historyData] = await Promise.all([
        locationService.getConsent(),
        locationService.getHistory(20),
      ]);
      setConsent(consentData);
      setHistory(historyData.logs);
    } catch (error) {
      Alert.alert('오류', '위치정보 설정을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConsentChange = async (value: boolean) => {
    if (value && !hasPermission) {
      const granted = await requestPermission();
      if (!granted) {
        Alert.alert(
          '위치 권한 필요',
          '위치정보 공유를 사용하려면 설정에서 위치 권한을 허용해주세요.'
        );
        return;
      }
    }

    if (value) {
      Alert.alert(
        '위치정보 공유 동의',
        '긴급 상황(SOS, 미체크 알림) 시 비상 연락처에게 현재 위치가 전달됩니다.\n\n위치정보는 알림 발송 시에만 수집되며, 실시간 추적되지 않습니다.',
        [
          { text: '취소', style: 'cancel' },
          {
            text: '동의',
            onPress: () => updateConsent(true),
          },
        ]
      );
    } else {
      Alert.alert(
        '위치정보 공유 철회',
        '위치정보 공유를 중지하시겠습니까?\n비상 알림에 위치정보가 포함되지 않습니다.',
        [
          { text: '취소', style: 'cancel' },
          {
            text: '철회',
            style: 'destructive',
            onPress: () => updateConsent(false),
          },
        ]
      );
    }
  };

  const updateConsent = async (value: boolean) => {
    setIsUpdating(true);
    try {
      const result = await locationService.updateConsent(value);
      setConsent(result);
    } catch (error) {
      Alert.alert('오류', '설정 변경에 실패했습니다.');
    } finally {
      setIsUpdating(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getEventTypeLabel = (eventType: string) => {
    switch (eventType) {
      case 'sos':
        return 'SOS 알림';
      case 'missed_checkin':
        return '미체크 알림';
      default:
        return eventType;
    }
  };

  const renderHistoryItem = ({ item }: { item: LocationSharingLog }) => (
    <View style={styles.historyItem}>
      <View style={styles.historyIcon}>
        <Ionicons
          name={item.eventType === 'sos' ? 'warning' : 'time'}
          size={20}
          color={item.eventType === 'sos' ? COLORS.error : COLORS.warning}
        />
      </View>
      <View style={styles.historyInfo}>
        <Text style={styles.historyType}>{getEventTypeLabel(item.eventType)}</Text>
        <Text style={styles.historyDate}>{formatDate(item.sharedAt)}</Text>
        {item.locationLat && item.locationLng && (
          <Text style={styles.historyLocation}>
            위치: {item.locationLat.toFixed(4)}, {item.locationLng.toFixed(4)}
          </Text>
        )}
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <Stack.Screen options={{ title: '위치정보 공유' }} />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.primary} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <>
      <Stack.Screen
        options={{
          title: '위치정보 공유',
          headerBackTitle: '설정',
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Info Banner */}
          <View style={styles.infoBanner}>
            <Ionicons name="location" size={24} color={COLORS.primary} />
            <Text style={styles.infoBannerText}>
              긴급 상황 시 비상연락처에게{'\n'}현재 위치를 공유합니다
            </Text>
          </View>

          {/* Consent Section */}
          <View style={styles.section}>
            <View style={styles.consentRow}>
              <View style={styles.consentInfo}>
                <Text style={styles.consentTitle}>위치정보 공유</Text>
                <Text style={styles.consentDesc}>
                  SOS 및 미체크 알림 시 위치정보 포함
                </Text>
              </View>
              <Switch
                value={consent?.locationConsent ?? false}
                onValueChange={handleConsentChange}
                trackColor={{ false: COLORS.border, true: COLORS.primaryLight }}
                thumbColor={consent?.locationConsent ? COLORS.primary : '#f4f3f4'}
                disabled={isUpdating}
              />
            </View>
            {consent?.locationConsentAt && (
              <Text style={styles.consentDate}>
                동의일: {formatDate(consent.locationConsentAt)}
              </Text>
            )}
          </View>

          {/* Explanation Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>위치정보 공유 안내</Text>

            <View style={styles.explainItem}>
              <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
              <Text style={styles.explainText}>
                SOS 버튼 발동 시 위치 전송
              </Text>
            </View>
            <View style={styles.explainItem}>
              <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
              <Text style={styles.explainText}>
                체크인 미완료 알림 시 위치 전송
              </Text>
            </View>
            <View style={styles.explainItem}>
              <Ionicons name="close-circle" size={20} color={COLORS.textTertiary} />
              <Text style={styles.explainTextDisabled}>
                실시간 위치 추적 없음
              </Text>
            </View>
            <View style={styles.explainItem}>
              <Ionicons name="shield-checkmark" size={20} color={COLORS.primary} />
              <Text style={styles.explainText}>
                위치정보는 6개월 후 자동 삭제
              </Text>
            </View>
          </View>

          {/* History Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>공유 기록</Text>
            {history.length === 0 ? (
              <Text style={styles.emptyHistory}>위치정보 공유 기록이 없습니다</Text>
            ) : (
              <FlatList
                data={history}
                renderItem={renderHistoryItem}
                keyExtractor={(item) => item.id}
                scrollEnabled={false}
              />
            )}
          </View>

          {/* Legal Notice */}
          <View style={styles.legalNotice}>
            <Ionicons name="information-circle" size={16} color={COLORS.textTertiary} />
            <Text style={styles.legalText}>
              위치정보법 제19조에 따라 위치정보 이용 및 제3자 제공 내역이 기록됩니다.
              언제든지 동의를 철회할 수 있습니다.
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    paddingBottom: SPACING.xl,
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primaryLight,
    padding: SPACING.lg,
    gap: SPACING.md,
  },
  infoBannerText: {
    flex: 1,
    fontSize: FONT_SIZES.md,
    color: COLORS.text,
    lineHeight: 22,
  },
  section: {
    backgroundColor: COLORS.surface,
    marginTop: SPACING.md,
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
  },
  sectionTitle: {
    fontSize: FONT_SIZES.sm,
    fontWeight: '600',
    color: COLORS.textSecondary,
    marginBottom: SPACING.md,
    textTransform: 'uppercase',
  },
  consentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  consentInfo: {
    flex: 1,
    marginRight: SPACING.md,
  },
  consentTitle: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: COLORS.text,
  },
  consentDesc: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  consentDate: {
    fontSize: FONT_SIZES.xs,
    color: COLORS.textTertiary,
    marginTop: SPACING.sm,
  },
  explainItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    gap: SPACING.sm,
  },
  explainText: {
    flex: 1,
    fontSize: FONT_SIZES.md,
    color: COLORS.text,
  },
  explainTextDisabled: {
    flex: 1,
    fontSize: FONT_SIZES.md,
    color: COLORS.textTertiary,
  },
  emptyHistory: {
    fontSize: FONT_SIZES.md,
    color: COLORS.textTertiary,
    textAlign: 'center',
    paddingVertical: SPACING.lg,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderLight,
  },
  historyIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  historyInfo: {
    flex: 1,
  },
  historyType: {
    fontSize: FONT_SIZES.md,
    fontWeight: '500',
    color: COLORS.text,
  },
  historyDate: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  historyLocation: {
    fontSize: FONT_SIZES.xs,
    color: COLORS.textTertiary,
    marginTop: 2,
  },
  legalNotice: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    gap: SPACING.xs,
  },
  legalText: {
    flex: 1,
    fontSize: FONT_SIZES.xs,
    color: COLORS.textTertiary,
    lineHeight: 16,
  },
});
