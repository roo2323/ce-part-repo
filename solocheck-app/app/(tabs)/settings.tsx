import { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useAuthStore } from '@/stores/auth.store';

type IconName = React.ComponentProps<typeof Ionicons>['name'];

interface SettingItem {
  id: string;
  title: string;
  subtitle?: string;
  icon: IconName;
  type: 'link' | 'toggle' | 'action';
  value?: boolean;
  onPress?: () => void;
  onToggle?: (value: boolean) => void;
  danger?: boolean;
}

export default function SettingsScreen() {
  const { user, logout } = useAuthStore();
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [reminderEnabled, setReminderEnabled] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      '로그아웃',
      '정말 로그아웃 하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '로그아웃',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/(auth)/login');
          },
        },
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      '계정 삭제',
      '정말 계정을 삭제하시겠습니까?\n삭제된 계정은 복구할 수 없습니다.',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: () => {
            Alert.alert('알림', '계정 삭제 기능은 준비 중입니다.');
          },
        },
      ]
    );
  };

  const settingSections: { title: string; items: SettingItem[] }[] = [
    {
      title: '알림 설정',
      items: [
        {
          id: 'notifications',
          title: '푸시 알림',
          subtitle: '체크인 알림을 받습니다',
          icon: 'notifications-outline',
          type: 'toggle',
          value: notificationsEnabled,
          onToggle: setNotificationsEnabled,
        },
        {
          id: 'reminder',
          title: '체크인 리마인더',
          subtitle: '체크인 시간이 되면 알려드립니다',
          icon: 'alarm-outline',
          type: 'toggle',
          value: reminderEnabled,
          onToggle: setReminderEnabled,
        },
        {
          id: 'reminder-settings',
          title: '리마인더 설정',
          subtitle: '알림 시간, 방해금지 시간 등을 설정합니다',
          icon: 'options-outline',
          type: 'link',
          onPress: () => router.push('/settings/reminder'),
        },
      ],
    },
    {
      title: '체크인 설정',
      items: [
        {
          id: 'checkin-interval',
          title: '체크인 주기',
          subtitle: '현재: 24시간',
          icon: 'time-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '체크인 주기 설정은 준비 중입니다.'),
        },
        {
          id: 'grace-period',
          title: '유예 기간',
          subtitle: '현재: 12시간',
          icon: 'hourglass-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '유예 기간 설정은 준비 중입니다.'),
        },
      ],
    },
    {
      title: '비상 정보',
      items: [
        {
          id: 'info-vault',
          title: '정보 금고',
          subtitle: '의료, 주거, 보험 등 중요 정보 관리',
          icon: 'lock-closed-outline',
          type: 'link',
          onPress: () => router.push('/settings/vault'),
        },
        {
          id: 'location-sharing',
          title: '위치정보 공유',
          subtitle: '비상 알림 시 위치 전송 설정',
          icon: 'location-outline',
          type: 'link',
          onPress: () => router.push('/settings/location'),
        },
      ],
    },
    {
      title: '계정',
      items: [
        {
          id: 'profile',
          title: '프로필 수정',
          icon: 'person-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '프로필 수정은 준비 중입니다.'),
        },
        {
          id: 'password',
          title: '비밀번호 변경',
          icon: 'lock-closed-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '비밀번호 변경은 준비 중입니다.'),
        },
        {
          id: 'logout',
          title: '로그아웃',
          icon: 'log-out-outline',
          type: 'action',
          onPress: handleLogout,
        },
      ],
    },
    {
      title: '정보',
      items: [
        {
          id: 'terms',
          title: '이용약관',
          icon: 'document-text-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '이용약관 페이지는 준비 중입니다.'),
        },
        {
          id: 'privacy',
          title: '개인정보 처리방침',
          icon: 'shield-checkmark-outline',
          type: 'link',
          onPress: () => Alert.alert('알림', '개인정보 처리방침 페이지는 준비 중입니다.'),
        },
        {
          id: 'version',
          title: '앱 버전',
          subtitle: '1.0.0',
          icon: 'information-circle-outline',
          type: 'link',
        },
      ],
    },
    {
      title: '위험 영역',
      items: [
        {
          id: 'delete-account',
          title: '계정 삭제',
          icon: 'trash-outline',
          type: 'action',
          onPress: handleDeleteAccount,
          danger: true,
        },
      ],
    },
  ];

  const renderSettingItem = (item: SettingItem) => (
    <TouchableOpacity
      key={item.id}
      style={styles.settingItem}
      onPress={item.type === 'toggle' ? undefined : item.onPress}
      disabled={item.type === 'toggle'}
      activeOpacity={item.type === 'toggle' ? 1 : 0.7}
    >
      <View style={styles.settingItemLeft}>
        <View style={[styles.iconContainer, item.danger && styles.iconContainerDanger]}>
          <Ionicons
            name={item.icon}
            size={20}
            color={item.danger ? '#ff3b30' : '#007AFF'}
          />
        </View>
        <View style={styles.settingItemContent}>
          <Text style={[styles.settingItemTitle, item.danger && styles.settingItemTitleDanger]}>
            {item.title}
          </Text>
          {item.subtitle && (
            <Text style={styles.settingItemSubtitle}>{item.subtitle}</Text>
          )}
        </View>
      </View>
      {item.type === 'toggle' && item.onToggle && (
        <Switch
          value={item.value}
          onValueChange={item.onToggle}
          trackColor={{ false: '#e0e0e0', true: '#007AFF' }}
          thumbColor="#ffffff"
        />
      )}
      {item.type === 'link' && (
        <Ionicons name="chevron-forward" size={20} color="#ccc" />
      )}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.profileCard}>
          <View style={styles.avatar}>
            <Ionicons name="person" size={32} color="#007AFF" />
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{user?.name || '사용자'}</Text>
            <Text style={styles.profileEmail}>{user?.email || ''}</Text>
          </View>
        </View>

        {settingSections.map((section) => (
          <View key={section.title} style={styles.section}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.sectionContent}>
              {section.items.map(renderSettingItem)}
            </View>
          </View>
        ))}
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
    paddingBottom: 32,
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    padding: 20,
    marginBottom: 24,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#e8f4ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileInfo: {
    marginLeft: 16,
    flex: 1,
  },
  profileName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  profileEmail: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  sectionContent: {
    backgroundColor: '#ffffff',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingItemLeft: {
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
  iconContainerDanger: {
    backgroundColor: '#ffebeb',
  },
  settingItemContent: {
    flex: 1,
  },
  settingItemTitle: {
    fontSize: 16,
    color: '#333',
  },
  settingItemTitleDanger: {
    color: '#ff3b30',
  },
  settingItemSubtitle: {
    fontSize: 13,
    color: '#999',
    marginTop: 2,
  },
});
