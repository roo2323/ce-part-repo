import { Stack } from 'expo-router';

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerBackTitle: '뒤로',
        headerTitleAlign: 'center',
        headerStyle: {
          backgroundColor: '#ffffff',
        },
        headerTintColor: '#007AFF',
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <Stack.Screen
        name="login"
        options={{
          title: '로그인',
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="register"
        options={{
          title: '회원가입',
        }}
      />
    </Stack>
  );
}
