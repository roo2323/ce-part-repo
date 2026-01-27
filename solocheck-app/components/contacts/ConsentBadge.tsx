import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ConsentStatus } from '@/types';

interface ConsentBadgeProps {
  status: ConsentStatus;
  compact?: boolean;
}

const STATUS_CONFIG: Record<
  ConsentStatus,
  {
    label: string;
    color: string;
    backgroundColor: string;
    icon: React.ComponentProps<typeof Ionicons>['name'];
  }
> = {
  pending: {
    label: '대기중',
    color: '#FF9500',
    backgroundColor: '#FFF3E0',
    icon: 'time-outline',
  },
  approved: {
    label: '승인됨',
    color: '#34C759',
    backgroundColor: '#E8F5E9',
    icon: 'checkmark-circle-outline',
  },
  rejected: {
    label: '거부됨',
    color: '#FF3B30',
    backgroundColor: '#FFEBEE',
    icon: 'close-circle-outline',
  },
  expired: {
    label: '만료됨',
    color: '#8E8E93',
    backgroundColor: '#F2F2F7',
    icon: 'alert-circle-outline',
  },
};

export default function ConsentBadge({ status, compact = false }: ConsentBadgeProps) {
  const config = STATUS_CONFIG[status];

  if (compact) {
    return (
      <View style={[styles.compactBadge, { backgroundColor: config.backgroundColor }]}>
        <Ionicons name={config.icon} size={12} color={config.color} />
      </View>
    );
  }

  return (
    <View style={[styles.badge, { backgroundColor: config.backgroundColor }]}>
      <Ionicons name={config.icon} size={14} color={config.color} />
      <Text style={[styles.badgeText, { color: config.color }]}>{config.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '500',
  },
  compactBadge: {
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
