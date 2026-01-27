import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

type IconName = React.ComponentProps<typeof Ionicons>['name'];

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopColor: '#eee',
          paddingBottom: 4,
          paddingTop: 4,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerStyle: {
          backgroundColor: '#ffffff',
        },
        headerTintColor: '#333',
        headerTitleStyle: {
          fontWeight: '600',
        },
        headerTitleAlign: 'center',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '홈',
          tabBarIcon: ({ color, size }: { color: string; size: number }) => (
            <Ionicons name="home-outline" size={size} color={color} />
          ),
          headerTitle: '하루안부',
        }}
      />
      <Tabs.Screen
        name="contacts"
        options={{
          title: '비상연락처',
          tabBarIcon: ({ color, size }: { color: string; size: number }) => (
            <Ionicons name="people-outline" size={size} color={color} />
          ),
          headerTitle: '비상연락처 관리',
        }}
      />
      <Tabs.Screen
        name="pets"
        options={{
          title: '반려동물',
          tabBarIcon: ({ color, size }: { color: string; size: number }) => (
            <Ionicons name="paw-outline" size={size} color={color} />
          ),
          headerTitle: '반려동물 정보',
        }}
      />
      <Tabs.Screen
        name="message"
        options={{
          title: '메시지',
          tabBarIcon: ({ color, size }: { color: string; size: number }) => (
            <Ionicons name="mail-outline" size={size} color={color} />
          ),
          headerTitle: '개인 메시지 설정',
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: '설정',
          tabBarIcon: ({ color, size }: { color: string; size: number }) => (
            <Ionicons name="settings-outline" size={size} color={color} />
          ),
          headerTitle: '설정',
        }}
      />
    </Tabs>
  );
}
