import { Stack } from 'expo-router';

export default function SettingsLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerBackTitle: '설정',
        headerTitleAlign: 'center',
        headerStyle: {
          backgroundColor: '#ffffff',
        },
        headerTintColor: '#333',
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <Stack.Screen name="profile" options={{ title: '프로필 수정' }} />
      <Stack.Screen name="password" options={{ title: '비밀번호 변경' }} />
      <Stack.Screen name="checkin" options={{ title: '체크인 주기' }} />
      <Stack.Screen name="reminder" options={{ title: '리마인더 설정' }} />
      <Stack.Screen name="vault/index" options={{ title: '정보 금고' }} />
      <Stack.Screen name="vault/add" options={{ title: '정보 추가' }} />
      <Stack.Screen name="vault/[id]" options={{ title: '정보 수정' }} />
      <Stack.Screen name="location" options={{ title: '위치정보 공유' }} />
      <Stack.Screen name="terms" options={{ title: '이용약관' }} />
      <Stack.Screen name="privacy" options={{ title: '개인정보 처리방침' }} />
    </Stack>
  );
}
