import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, Stack } from 'expo-router';
import { useVaultStore } from '@/stores/vault.store';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '@/constants';
import type { VaultCategory, CreateVaultRequest } from '@/types';

const CATEGORY_OPTIONS: { value: VaultCategory; label: string; icon: string }[] = [
  { value: 'medical', label: '의료 정보', icon: 'medkit' },
  { value: 'housing', label: '주거 정보', icon: 'home' },
  { value: 'insurance', label: '보험 정보', icon: 'shield-checkmark' },
  { value: 'financial', label: '금융 정보', icon: 'card' },
  { value: 'other', label: '기타', icon: 'document-text' },
];

export default function AddVaultItemScreen() {
  const router = useRouter();
  const { createVaultItem, isLoading } = useVaultStore();

  const [category, setCategory] = useState<VaultCategory>('medical');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [includeInAlert, setIncludeInAlert] = useState(false);

  const handleSave = async () => {
    if (!title.trim()) {
      Alert.alert('입력 오류', '제목을 입력해주세요.');
      return;
    }
    if (!content.trim()) {
      Alert.alert('입력 오류', '내용을 입력해주세요.');
      return;
    }

    const data: CreateVaultRequest = {
      category,
      title: title.trim(),
      content: content.trim(),
      include_in_alert: includeInAlert,
    };

    try {
      await createVaultItem(data);
      Alert.alert('저장 완료', '정보가 안전하게 저장되었습니다.', [
        { text: '확인', onPress: () => router.back() },
      ]);
    } catch (error) {
      Alert.alert('오류', error instanceof Error ? error.message : '저장에 실패했습니다.');
    }
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: '정보 추가',
          headerBackTitle: '취소',
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>카테고리</Text>
            <View style={styles.categoryGrid}>
              {CATEGORY_OPTIONS.map((option) => (
                <TouchableOpacity
                  key={option.value}
                  style={[
                    styles.categoryButton,
                    category === option.value && styles.categoryButtonActive,
                  ]}
                  onPress={() => setCategory(option.value)}
                >
                  <Ionicons
                    name={option.icon as any}
                    size={24}
                    color={category === option.value ? COLORS.primary : COLORS.textSecondary}
                  />
                  <Text
                    style={[
                      styles.categoryButtonText,
                      category === option.value && styles.categoryButtonTextActive,
                    ]}
                  >
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>정보 입력</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>제목 *</Text>
              <TextInput
                style={styles.input}
                value={title}
                onChangeText={setTitle}
                placeholder="예: 혈액형, 관리사무소 연락처"
                placeholderTextColor={COLORS.textTertiary}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>내용 *</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={content}
                onChangeText={setContent}
                placeholder="중요한 정보를 입력해주세요"
                placeholderTextColor={COLORS.textTertiary}
                multiline
                numberOfLines={6}
              />
            </View>
          </View>

          <View style={styles.section}>
            <View style={styles.toggleRow}>
              <View style={styles.toggleInfo}>
                <Text style={styles.toggleLabel}>비상 알림에 포함</Text>
                <Text style={styles.toggleDesc}>
                  체크인 미완료 시 연락처에 이 정보가 전달됩니다
                </Text>
              </View>
              <Switch
                value={includeInAlert}
                onValueChange={setIncludeInAlert}
                trackColor={{ false: COLORS.border, true: COLORS.primaryLight }}
                thumbColor={includeInAlert ? COLORS.primary : '#f4f3f4'}
              />
            </View>
            {includeInAlert && (
              <View style={styles.warningBox}>
                <Ionicons name="warning" size={16} color={COLORS.warning} />
                <Text style={styles.warningText}>
                  이 정보가 비상 연락처에게 전달됩니다
                </Text>
              </View>
            )}
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}
            onPress={handleSave}
            disabled={isLoading}
          >
            <Ionicons name="lock-closed" size={20} color="#fff" />
            <Text style={styles.saveButtonText}>
              {isLoading ? '저장 중...' : '암호화하여 저장'}
            </Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    paddingBottom: SPACING.xl,
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
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  categoryButton: {
    width: '48%',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    backgroundColor: COLORS.background,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: SPACING.sm,
  },
  categoryButtonActive: {
    backgroundColor: COLORS.primaryLight,
    borderColor: COLORS.primary,
  },
  categoryButtonText: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
  },
  categoryButtonTextActive: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  inputGroup: {
    marginBottom: SPACING.md,
  },
  label: {
    fontSize: FONT_SIZES.sm,
    fontWeight: '500',
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  input: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    fontSize: FONT_SIZES.md,
    color: COLORS.text,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  textArea: {
    minHeight: 150,
    textAlignVertical: 'top',
    paddingTop: SPACING.sm,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleInfo: {
    flex: 1,
    marginRight: SPACING.md,
  },
  toggleLabel: {
    fontSize: FONT_SIZES.md,
    fontWeight: '500',
    color: COLORS.text,
  },
  toggleDesc: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  warningBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff8e6',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.sm,
    marginTop: SPACING.md,
    gap: SPACING.xs,
  },
  warningText: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.warning,
    flex: 1,
  },
  footer: {
    padding: SPACING.lg,
    backgroundColor: COLORS.surface,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderLight,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.lg,
    paddingVertical: SPACING.md,
    gap: SPACING.sm,
  },
  saveButtonDisabled: {
    backgroundColor: COLORS.disabled,
  },
  saveButtonText: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: '#fff',
  },
});
