import { useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useCheckinStore } from '@/stores/checkin.store';
import { useAuthStore } from '@/stores/auth.store';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES, LEGAL_NOTICE } from '@/constants';

export default function HomeScreen() {
  const { user } = useAuthStore();
  const { status, checkIn, fetchStatus, isLoading, error } = useCheckinStore();

  useEffect(() => {
    fetchStatus();
  }, []);

  const onRefresh = useCallback(() => {
    fetchStatus();
  }, []);

  const handleCheckIn = async () => {
    try {
      await checkIn();
      Alert.alert('체크인 완료', '오늘의 체크인이 완료되었습니다. 안전을 알려주셔서 감사합니다.');
    } catch (err) {
      Alert.alert(
        '체크인 실패',
        err instanceof Error ? err.message : '체크인에 실패했습니다. 다시 시도해주세요.'
      );
    }
  };

  const formatLastCheckinTime = () => {
    if (!status?.lastCheckin) return null;
    const date = new Date(status.lastCheckin.checkedAt);
    return date.toLocaleString('ko-KR', {
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getDaysRemaining = () => {
    if (status?.daysRemaining === null || status?.daysRemaining === undefined) {
      return status?.checkinCycleDays ?? 7;
    }
    return Math.max(0, status.daysRemaining);
  };

  const getStatusMessage = () => {
    if (!status?.lastCheckin) {
      return '아직 체크인 기록이 없습니다';
    }
    if (status.isOverdue) {
      return '체크인 기한이 지났습니다';
    }
    const days = getDaysRemaining();
    if (days === 0) {
      return '오늘 체크인이 필요합니다';
    }
    return '다음 체크인까지';
  };

  const getStatusColor = () => {
    if (!status?.lastCheckin || status?.isOverdue) {
      return COLORS.error;
    }
    const days = getDaysRemaining();
    if (days <= 1) {
      return COLORS.warning;
    }
    return COLORS.primary;
  };

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={onRefresh}
            tintColor={COLORS.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Greeting Section */}
        <View style={styles.greetingSection}>
          <Text style={styles.greetingText}>
            안녕하세요, {user?.name || '사용자'}님
          </Text>
          <Text style={styles.greetingSubtext}>
            오늘도 무사한 하루 보내세요
          </Text>
        </View>

        {/* Main Status Card */}
        <View style={styles.statusCard}>
          <Text style={[styles.statusMessage, { color: getStatusColor() }]}>
            {getStatusMessage()}
          </Text>

          <View style={styles.daysContainer}>
            <Text style={[styles.daysNumber, { color: getStatusColor() }]}>
              {getDaysRemaining()}
            </Text>
            <Text style={styles.daysUnit}>일</Text>
          </View>

          {status?.lastCheckin && (
            <View style={styles.lastCheckinInfo}>
              <Ionicons name="time-outline" size={16} color={COLORS.textTertiary} />
              <Text style={styles.lastCheckinText}>
                마지막 체크인: {formatLastCheckinTime()}
              </Text>
            </View>
          )}
        </View>

        {/* Check-in Button */}
        <TouchableOpacity
          style={[
            styles.checkInButton,
            isLoading && styles.checkInButtonDisabled,
          ]}
          onPress={handleCheckIn}
          disabled={isLoading}
          activeOpacity={0.8}
        >
          <Ionicons
            name="checkmark-circle"
            size={32}
            color={COLORS.surface}
            style={styles.checkInIcon}
          />
          <Text style={styles.checkInButtonText}>
            {isLoading ? '처리 중...' : '괜찮아요'}
          </Text>
          <Text style={styles.checkInSubtext}>
            탭하여 안전을 알려주세요
          </Text>
        </TouchableOpacity>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <View style={styles.infoHeader}>
            <Ionicons name="information-circle-outline" size={20} color={COLORS.primary} />
            <Text style={styles.infoTitle}>서비스 안내</Text>
          </View>
          <Text style={styles.infoText}>
            정해진 기간({status?.checkinCycleDays ?? 7}일) 동안 체크인이 없으면
            등록된 비상연락처에 알림이 전송됩니다.
            정기적으로 체크인하여 소중한 사람들에게 안심을 전해주세요.
          </Text>
        </View>

        {/* Settings Summary */}
        <View style={styles.settingsSummary}>
          <View style={styles.settingItem}>
            <Ionicons name="calendar-outline" size={18} color={COLORS.textSecondary} />
            <Text style={styles.settingLabel}>체크인 주기</Text>
            <Text style={styles.settingValue}>{status?.checkinCycleDays ?? 7}일</Text>
          </View>
          <View style={styles.settingDivider} />
          <View style={styles.settingItem}>
            <Ionicons name="hourglass-outline" size={18} color={COLORS.textSecondary} />
            <Text style={styles.settingLabel}>유예 기간</Text>
            <Text style={styles.settingValue}>{status?.gracePeriodHours ?? 24}시간</Text>
          </View>
        </View>
      </ScrollView>

      {/* Footer with Legal Notice */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          {LEGAL_NOTICE.short}
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.md,
    paddingBottom: SPACING.lg,
  },
  greetingSection: {
    marginBottom: SPACING.lg,
  },
  greetingText: {
    fontSize: FONT_SIZES.title,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  greetingSubtext: {
    fontSize: FONT_SIZES.md,
    color: COLORS.textSecondary,
    marginTop: SPACING.xs,
  },
  statusCard: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.xl,
    padding: SPACING.xl,
    alignItems: 'center',
    marginBottom: SPACING.lg,
    shadowColor: COLORS.cardShadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 4,
  },
  statusMessage: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    marginBottom: SPACING.sm,
  },
  daysContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginVertical: SPACING.md,
  },
  daysNumber: {
    fontSize: FONT_SIZES.display,
    fontWeight: 'bold',
    lineHeight: 72,
  },
  daysUnit: {
    fontSize: FONT_SIZES.xxl,
    fontWeight: '600',
    color: COLORS.textSecondary,
    marginLeft: SPACING.xs,
  },
  lastCheckinInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.sm,
  },
  lastCheckinText: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textTertiary,
    marginLeft: SPACING.xs,
  },
  checkInButton: {
    backgroundColor: COLORS.checkinButton,
    borderRadius: BORDER_RADIUS.xl,
    paddingVertical: SPACING.xl,
    paddingHorizontal: SPACING.xl,
    alignItems: 'center',
    marginBottom: SPACING.lg,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 6,
  },
  checkInButtonDisabled: {
    backgroundColor: COLORS.disabled,
    shadowOpacity: 0.1,
  },
  checkInIcon: {
    marginBottom: SPACING.sm,
  },
  checkInButtonText: {
    fontSize: FONT_SIZES.heading,
    fontWeight: 'bold',
    color: COLORS.surface,
  },
  checkInSubtext: {
    fontSize: FONT_SIZES.md,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: SPACING.xs,
  },
  infoCard: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  infoTitle: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: COLORS.text,
    marginLeft: SPACING.sm,
  },
  infoText: {
    fontSize: FONT_SIZES.md,
    color: COLORS.textSecondary,
    lineHeight: 22,
  },
  settingsSummary: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    shadowColor: COLORS.cardShadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  settingItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingLabel: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginLeft: SPACING.xs,
  },
  settingValue: {
    fontSize: FONT_SIZES.md,
    fontWeight: '600',
    color: COLORS.text,
    marginLeft: SPACING.xs,
  },
  settingDivider: {
    width: 1,
    backgroundColor: COLORS.border,
    marginVertical: SPACING.xs,
  },
  footer: {
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderLight,
    backgroundColor: COLORS.surface,
  },
  footerText: {
    fontSize: FONT_SIZES.xs,
    color: COLORS.textTertiary,
    textAlign: 'center',
    lineHeight: 16,
  },
});
