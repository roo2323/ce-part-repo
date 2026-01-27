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
import { usePetStore } from '@/stores/pet.store';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '@/constants';
import type { PetSpecies, CreatePetRequest } from '@/types';

const SPECIES_OPTIONS: { value: PetSpecies; label: string }[] = [
  { value: 'dog', label: '강아지' },
  { value: 'cat', label: '고양이' },
  { value: 'bird', label: '새' },
  { value: 'fish', label: '물고기' },
  { value: 'reptile', label: '파충류' },
  { value: 'small_animal', label: '소동물' },
  { value: 'other', label: '기타' },
];

export default function AddPetScreen() {
  const router = useRouter();
  const { createPet, isLoading } = usePetStore();

  const [name, setName] = useState('');
  const [species, setSpecies] = useState<PetSpecies>('dog');
  const [breed, setBreed] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [weight, setWeight] = useState('');
  const [medicalNotes, setMedicalNotes] = useState('');
  const [vetInfo, setVetInfo] = useState('');
  const [caretakerContact, setCaretakerContact] = useState('');
  const [includeInAlert, setIncludeInAlert] = useState(true);

  const handleSave = async () => {
    if (!name.trim()) {
      Alert.alert('입력 오류', '반려동물 이름을 입력해주세요.');
      return;
    }

    const data: CreatePetRequest = {
      name: name.trim(),
      species,
      include_in_alert: includeInAlert,
    };

    if (breed.trim()) data.breed = breed.trim();
    if (birthDate.trim()) data.birth_date = birthDate.trim();
    if (weight.trim()) {
      const weightNum = parseFloat(weight);
      if (!isNaN(weightNum) && weightNum > 0) {
        data.weight = weightNum;
      }
    }
    if (medicalNotes.trim()) data.medical_notes = medicalNotes.trim();
    if (vetInfo.trim()) data.vet_info = vetInfo.trim();
    if (caretakerContact.trim()) data.caretaker_contact = caretakerContact.trim();

    try {
      await createPet(data);
      Alert.alert('등록 완료', '반려동물이 등록되었습니다.', [
        { text: '확인', onPress: () => router.back() },
      ]);
    } catch (error) {
      Alert.alert('오류', error instanceof Error ? error.message : '등록에 실패했습니다.');
    }
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: '반려동물 등록',
          headerBackTitle: '취소',
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ marginLeft: 8 }}>
              <Ionicons name="close" size={24} color={COLORS.text} />
            </TouchableOpacity>
          ),
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>기본 정보</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>이름 *</Text>
              <TextInput
                style={styles.input}
                value={name}
                onChangeText={setName}
                placeholder="반려동물 이름"
                placeholderTextColor={COLORS.textTertiary}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>종류 *</Text>
              <View style={styles.speciesGrid}>
                {SPECIES_OPTIONS.map((option) => (
                  <TouchableOpacity
                    key={option.value}
                    style={[
                      styles.speciesButton,
                      species === option.value && styles.speciesButtonActive,
                    ]}
                    onPress={() => setSpecies(option.value)}
                  >
                    <Text
                      style={[
                        styles.speciesButtonText,
                        species === option.value && styles.speciesButtonTextActive,
                      ]}
                    >
                      {option.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>품종</Text>
              <TextInput
                style={styles.input}
                value={breed}
                onChangeText={setBreed}
                placeholder="예: 말티즈, 페르시안"
                placeholderTextColor={COLORS.textTertiary}
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, { flex: 1 }]}>
                <Text style={styles.label}>생년월일</Text>
                <TextInput
                  style={styles.input}
                  value={birthDate}
                  onChangeText={setBirthDate}
                  placeholder="YYYY-MM-DD"
                  placeholderTextColor={COLORS.textTertiary}
                />
              </View>
              <View style={[styles.inputGroup, { flex: 1, marginLeft: SPACING.md }]}>
                <Text style={styles.label}>체중 (kg)</Text>
                <TextInput
                  style={styles.input}
                  value={weight}
                  onChangeText={setWeight}
                  placeholder="3.5"
                  keyboardType="decimal-pad"
                  placeholderTextColor={COLORS.textTertiary}
                />
              </View>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>건강 정보</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>건강 특이사항</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={medicalNotes}
                onChangeText={setMedicalNotes}
                placeholder="알레르기, 복용 약, 특별 케어 사항 등"
                placeholderTextColor={COLORS.textTertiary}
                multiline
                numberOfLines={3}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>단골 동물병원</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={vetInfo}
                onChangeText={setVetInfo}
                placeholder="병원명, 연락처 등"
                placeholderTextColor={COLORS.textTertiary}
                multiline
                numberOfLines={2}
              />
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>긴급 연락처</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>긴급 시 돌봐줄 분 연락처</Text>
              <TextInput
                style={styles.input}
                value={caretakerContact}
                onChangeText={setCaretakerContact}
                placeholder="이름 및 전화번호"
                placeholderTextColor={COLORS.textTertiary}
              />
            </View>
          </View>

          <View style={styles.section}>
            <View style={styles.toggleRow}>
              <View style={styles.toggleInfo}>
                <Text style={styles.toggleLabel}>비상 알림에 포함</Text>
                <Text style={styles.toggleDesc}>
                  체크인 미완료 시 연락처에 반려동물 정보가 전달됩니다
                </Text>
              </View>
              <Switch
                value={includeInAlert}
                onValueChange={setIncludeInAlert}
                trackColor={{ false: COLORS.border, true: COLORS.primaryLight }}
                thumbColor={includeInAlert ? COLORS.primary : '#f4f3f4'}
              />
            </View>
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <View style={styles.footerButtons}>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => router.back()}
              disabled={isLoading}
            >
              <Text style={styles.cancelButtonText}>취소</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}
              onPress={handleSave}
              disabled={isLoading}
            >
              <Text style={styles.saveButtonText}>
                {isLoading ? '등록 중...' : '등록하기'}
              </Text>
            </TouchableOpacity>
          </View>
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
    minHeight: 80,
    textAlignVertical: 'top',
    paddingTop: SPACING.sm,
  },
  row: {
    flexDirection: 'row',
  },
  speciesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  speciesButton: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    backgroundColor: COLORS.background,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  speciesButtonActive: {
    backgroundColor: COLORS.primaryLight,
    borderColor: COLORS.primary,
  },
  speciesButtonText: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
  },
  speciesButtonTextActive: {
    color: COLORS.primary,
    fontWeight: '600',
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
  footer: {
    padding: SPACING.lg,
    backgroundColor: COLORS.surface,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderLight,
  },
  footerButtons: {
    flexDirection: 'row',
    gap: SPACING.md,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.lg,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  cancelButtonText: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: COLORS.textSecondary,
  },
  saveButton: {
    flex: 2,
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.lg,
    paddingVertical: SPACING.md,
    alignItems: 'center',
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
