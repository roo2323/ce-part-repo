import { useEffect, useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { usePetStore } from '@/stores/pet.store';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '@/constants';
import type { Pet, PetSpecies } from '@/types';

const SPECIES_LABELS: Record<PetSpecies, string> = {
  dog: '강아지',
  cat: '고양이',
  bird: '새',
  fish: '물고기',
  reptile: '파충류',
  small_animal: '소동물',
  other: '기타',
};

const SPECIES_ICONS: Record<PetSpecies, string> = {
  dog: 'paw',
  cat: 'paw',
  bird: 'leaf',
  fish: 'water',
  reptile: 'bug',
  small_animal: 'paw',
  other: 'help-circle',
};

export default function PetsScreen() {
  const router = useRouter();
  const { pets, isLoading, fetchPets, deletePet } = usePetStore();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchPets();
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await fetchPets();
    } finally {
      setRefreshing(false);
    }
  }, [fetchPets]);

  const handleAddPet = () => {
    router.push('/pets/add');
  };

  const handlePetPress = (petId: string) => {
    router.push(`/pets/${petId}`);
  };

  const handleDeletePet = (pet: Pet) => {
    Alert.alert(
      '반려동물 삭제',
      `${pet.name}를(을) 삭제하시겠습니까?`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              await deletePet(pet.id);
            } catch (error) {
              Alert.alert('오류', '반려동물 삭제에 실패했습니다.');
            }
          },
        },
      ]
    );
  };

  const calculateAge = (birthDate?: string): string | null => {
    if (!birthDate) return null;
    const birth = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    if (
      today.getMonth() < birth.getMonth() ||
      (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())
    ) {
      age--;
    }
    return `${age}살`;
  };

  const renderPetCard = ({ item: pet }: { item: Pet }) => (
    <TouchableOpacity
      style={styles.petCard}
      onPress={() => handlePetPress(pet.id)}
      activeOpacity={0.7}
    >
      <View style={styles.petIconContainer}>
        <Ionicons
          name={SPECIES_ICONS[pet.species] as any}
          size={28}
          color={COLORS.primary}
        />
      </View>
      <View style={styles.petInfo}>
        <View style={styles.petHeader}>
          <Text style={styles.petName}>{pet.name}</Text>
          {pet.includeInAlert && (
            <View style={styles.alertBadge}>
              <Ionicons name="notifications" size={12} color="#fff" />
            </View>
          )}
        </View>
        <Text style={styles.petSpecies}>
          {SPECIES_LABELS[pet.species]}
          {pet.breed && ` (${pet.breed})`}
          {pet.birthDate && ` · ${calculateAge(pet.birthDate)}`}
        </Text>
        {pet.medicalNotes && (
          <Text style={styles.petNotes} numberOfLines={1}>
            {pet.medicalNotes}
          </Text>
        )}
      </View>
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => handleDeletePet(pet)}
      >
        <Ionicons name="trash-outline" size={20} color={COLORS.error} />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="paw-outline" size={64} color={COLORS.textTertiary} />
      <Text style={styles.emptyTitle}>등록된 반려동물이 없습니다</Text>
      <Text style={styles.emptySubtitle}>
        반려동물 정보를 등록하면 비상 알림에 포함됩니다
      </Text>
      <TouchableOpacity style={styles.addButtonLarge} onPress={handleAddPet}>
        <Ionicons name="add" size={24} color="#fff" />
        <Text style={styles.addButtonLargeText}>반려동물 등록하기</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <View style={styles.infoCard}>
        <Ionicons name="information-circle-outline" size={20} color={COLORS.primary} />
        <Text style={styles.infoText}>
          반려동물 정보는 비상 알림 발송 시 연락처에 함께 전달됩니다.
        </Text>
      </View>

      <FlatList
        data={pets}
        renderItem={renderPetCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={[
          styles.listContent,
          pets.length === 0 && styles.emptyListContent,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={COLORS.primary}
          />
        }
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
      />

      {pets.length > 0 && (
        <TouchableOpacity style={styles.fab} onPress={handleAddPet}>
          <Ionicons name="add" size={28} color="#fff" />
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  infoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primaryLight,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    marginHorizontal: SPACING.md,
    marginTop: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    gap: SPACING.sm,
  },
  infoText: {
    flex: 1,
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    lineHeight: 18,
  },
  listContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  emptyListContent: {
    flex: 1,
    justifyContent: 'center',
  },
  petCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    shadowColor: COLORS.cardShadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  petIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  petInfo: {
    flex: 1,
  },
  petHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  petName: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: COLORS.text,
  },
  alertBadge: {
    backgroundColor: COLORS.primary,
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  petSpecies: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  petNotes: {
    fontSize: FONT_SIZES.xs,
    color: COLORS.textTertiary,
    marginTop: 4,
  },
  deleteButton: {
    padding: SPACING.sm,
  },
  emptyState: {
    alignItems: 'center',
    paddingHorizontal: SPACING.xl,
  },
  emptyTitle: {
    fontSize: FONT_SIZES.lg,
    fontWeight: '600',
    color: COLORS.text,
    marginTop: SPACING.md,
  },
  emptySubtitle: {
    fontSize: FONT_SIZES.md,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: SPACING.xs,
    lineHeight: 22,
  },
  addButtonLarge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    borderRadius: BORDER_RADIUS.lg,
    marginTop: SPACING.lg,
    gap: SPACING.sm,
  },
  addButtonLargeText: {
    fontSize: FONT_SIZES.md,
    fontWeight: '600',
    color: '#fff',
  },
  fab: {
    position: 'absolute',
    right: SPACING.lg,
    bottom: SPACING.lg,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
});
