---
name: ui-component
description: React Native 재사용 UI 컴포넌트 구현 시 사용. FRONTEND_DEV 전용. Button, Input 등 공통 컴포넌트.
---

# UI 컴포넌트 체크리스트

## 파일 구조
- [ ] `components/ui/{Component}.tsx` 위치
- [ ] 한 파일에 하나의 컴포넌트

## 컴포넌트 설계
- [ ] Props 인터페이스 정의
- [ ] 기본값 설정 (`defaultProps` 또는 파라미터 기본값)
- [ ] variant, size 등 변형 지원
- [ ] disabled 상태 지원

## 스타일
- [ ] `StyleSheet.create()` 사용
- [ ] 디자인 시스템 색상 사용
- [ ] variant별 스타일 분리

## TypeScript
- [ ] Props 인터페이스 export
- [ ] 명확한 타입 정의

---

## 디자인 시스템 색상
```typescript
export const colors = {
  primary: '#4F46E5',
  secondary: '#6B7280',
  danger: '#EF4444',
  success: '#10B981',
  warning: '#F59E0B',
  
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
};
```

## Button 템플릿
```tsx
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  style,
}: ButtonProps) {
  const isDisabled = disabled || isLoading;

  return (
    <TouchableOpacity
      style={[
        styles.base,
        styles[variant],
        styles[size],
        isDisabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.8}
    >
      {isLoading ? (
        <ActivityIndicator color={variant === 'outline' ? '#4F46E5' : '#fff'} />
      ) : (
        <Text style={[styles.text, styles[`${variant}Text`]]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: { backgroundColor: '#4F46E5' },
  secondary: { backgroundColor: '#6B7280' },
  danger: { backgroundColor: '#EF4444' },
  outline: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#4F46E5' },
  sm: { paddingVertical: 8, paddingHorizontal: 16 },
  md: { paddingVertical: 12, paddingHorizontal: 24 },
  lg: { paddingVertical: 16, paddingHorizontal: 32 },
  disabled: { opacity: 0.5 },
  text: { fontWeight: '600', fontSize: 16 },
  primaryText: { color: '#fff' },
  secondaryText: { color: '#fff' },
  dangerText: { color: '#fff' },
  outlineText: { color: '#4F46E5' },
});
```

## Input 템플릿
```tsx
import { View, Text, TextInput, StyleSheet, TextInputProps } from 'react-native';
import { useState } from 'react';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
}

export function Input({ label, error, helperText, style, ...props }: InputProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}
      <TextInput
        style={[
          styles.input,
          isFocused && styles.inputFocused,
          error && styles.inputError,
          style,
        ]}
        placeholderTextColor="#9CA3AF"
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        {...props}
      />
      {error && <Text style={styles.error}>{error}</Text>}
      {helperText && !error && <Text style={styles.helper}>{helperText}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '500', color: '#374151', marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: '#111827',
    backgroundColor: '#fff',
  },
  inputFocused: { borderColor: '#4F46E5' },
  inputError: { borderColor: '#EF4444' },
  error: { fontSize: 12, color: '#EF4444', marginTop: 4 },
  helper: { fontSize: 12, color: '#6B7280', marginTop: 4 },
});
```

---

## 완료 확인
- [ ] Props 인터페이스 정의
- [ ] variant/size 지원
- [ ] disabled/loading 상태
- [ ] TypeScript 타입 적용
