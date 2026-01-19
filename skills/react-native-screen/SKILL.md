---
name: react-native-screen
description: React Native 화면 컴포넌트 구현 시 사용. FRONTEND_DEV 전용. Expo Router 기반 Screen 작성.
---

# React Native 화면 컴포넌트 체크리스트

## 파일 구조
- [ ] 인증 화면: `app/(auth)/{screen}.tsx`
- [ ] 메인 화면: `app/(tabs)/{screen}.tsx`
- [ ] 모달/상세: `app/{screen}.tsx`

## 컴포넌트 구조
- [ ] 상태 관리: `useState`, `useEffect`
- [ ] 로딩 상태 처리
- [ ] 에러 상태 처리
- [ ] API 연동

## 스타일
- [ ] `StyleSheet.create()` 사용
- [ ] 컴포넌트 하단에 스타일 정의
- [ ] 색상은 디자인 시스템 상수 사용

## Expo Router
- [ ] `useFocusEffect` - 화면 포커스 시 새로고침
- [ ] `useRouter` - 네비게이션
- [ ] `useLocalSearchParams` - 파라미터

## TypeScript
- [ ] Props 타입 정의
- [ ] API 응답 타입 import

---

## Screen 템플릿
```tsx
import { useState, useEffect, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { useFocusEffect } from 'expo-router';

import { {Resource}Card } from '@/components/{resource}/{Resource}Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { {resource}Service } from '@/services/{resource}.service';
import type { {Resource}, {Resource}ListResponse } from '@/types/{resource}';

export default function {Resource}Screen() {
  const [data, setData] = useState<{Resource}ListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async (showRefresh = false) => {
    try {
      if (showRefresh) setIsRefreshing(true);
      else setIsLoading(true);
      setError(null);
      
      const result = await {resource}Service.getAll();
      setData(result);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // 화면 포커스 시 새로고침
  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <EmptyState
        icon="alert-circle"
        title="오류 발생"
        message={error}
        actionLabel="다시 시도"
        onAction={() => loadData()}
      />
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{화면 제목}</Text>
      </View>

      {data?.data.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="데이터가 없습니다"
          message="새로운 데이터를 추가해주세요"
        />
      ) : (
        <FlatList
          data={data?.data}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <{Resource}Card item={item} />}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={() => loadData(true)}
            />
          }
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  list: {
    padding: 16,
  },
});
```

---

## 완료 확인
- [ ] 로딩 상태 처리
- [ ] 에러 상태 처리
- [ ] 빈 상태 처리
- [ ] Pull to Refresh 구현
- [ ] TypeScript 타입 적용
