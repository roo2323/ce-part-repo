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
import { useRouter, Stack } from 'expo-router';
import { useVaultStore } from '@/stores/vault.store';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '@/constants';
import type { VaultItem, VaultCategory } from '@/types';

const CATEGORY_LABELS: Record<VaultCategory, string> = {
  medical: '의료 정보',
  housing: '주거 정보',
  insurance: '보험 정보',
  financial: '금융 정보',
  other: '기타',
};

const CATEGORY_ICONS: Record<VaultCategory, string> = {
  medical: 'medkit',
  housing: 'home',
  insurance: 'shield-checkmark',
  financial: 'card',
  other: 'document-text',
};

export default function VaultListScreen() {
  const router = useRouter();
  const { items, isLoading, fetchVaultItems, deleteVaultItem } = useVaultStore();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchVaultItems();
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await fetchVaultItems();
    } finally {
      setRefreshing(false);
    }
  }, [fetchVaultItems]);

  const handleAddItem = () => {
    router.push('/settings/vault/add');
  };

  const handleItemPress = (itemId: string) => {
    router.push(`/settings/vault/${itemId}`);
  };

  const handleDeleteItem = (item: VaultItem) => {
    Alert.alert(
      '정보 삭제',
      `"${item.title}"을(를) 삭제하시겠습니까?\n삭제된 정보는 복구할 수 없습니다.`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteVaultItem(item.id);
            } catch (error) {
              Alert.alert('오류', '정보 삭제에 실패했습니다.');
            }
          },
        },
      ]
    );
  };

  const renderVaultItem = ({ item }: { item: VaultItem }) => (
    <TouchableOpacity
      style={styles.itemCard}
      onPress={() => handleItemPress(item.id)}
      activeOpacity={0.7}
    >
      <View style={styles.itemIconContainer}>
        <Ionicons
          name={CATEGORY_ICONS[item.category] as any}
          size={24}
          color={COLORS.primary}
        />
      </View>
      <View style={styles.itemInfo}>
        <View style={styles.itemHeader}>
          <Text style={styles.itemTitle}>{item.title}</Text>
          {item.includeInAlert && (
            <View style={styles.alertBadge}>
              <Ionicons name="notifications" size={12} color="#fff" />
            </View>
          )}
        </View>
        <Text style={styles.itemCategory}>{CATEGORY_LABELS[item.category]}</Text>
      </View>
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => handleDeleteItem(item)}
      >
        <Ionicons name="trash-outline" size={20} color={COLORS.error} />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="lock-closed-outline" size={64} color={COLORS.textTertiary} />
      <Text style={styles.emptyTitle}>저장된 정보가 없습니다</Text>
      <Text style={styles.emptySubtitle}>
        의료, 주거, 보험 등 중요한 정보를 안전하게 보관하세요.
        {'\n'}비상 알림에 포함하여 전달할 수 있습니다.
      </Text>
      <TouchableOpacity style={styles.addButtonLarge} onPress={handleAddItem}>
        <Ionicons name="add" size={24} color="#fff" />
        <Text style={styles.addButtonLargeText}>정보 추가하기</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <>
      <Stack.Screen
        options={{
          title: '정보 금고',
          headerBackTitle: '설정',
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <View style={styles.infoCard}>
          <Ionicons name="shield-checkmark-outline" size={20} color={COLORS.primary} />
          <Text style={styles.infoText}>
            모든 정보는 암호화되어 안전하게 저장됩니다.
          </Text>
        </View>

        <FlatList
          data={items}
          renderItem={renderVaultItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={[
            styles.listContent,
            items.length === 0 && styles.emptyListContent,
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

        {items.length > 0 && (
          <TouchableOpacity style={styles.fab} onPress={handleAddItem}>
            <Ionicons name="add" size={28} color="#fff" />
          </TouchableOpacity>
        )}
      </SafeAreaView>
    </>
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
  },
  listContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  emptyListContent: {
    flex: 1,
    justifyContent: 'center',
  },
  itemCard: {
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
  itemIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  itemInfo: {
    flex: 1,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  itemTitle: {
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
  itemCategory: {
    fontSize: FONT_SIZES.sm,
    color: COLORS.textSecondary,
    marginTop: 2,
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
