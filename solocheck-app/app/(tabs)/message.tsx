import { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useMessageStore } from '@/stores/message.store';

const MAX_MESSAGE_LENGTH = 2000;

export default function MessageScreen() {
  const {
    message: savedMessageData,
    isLoading,
    isSaving,
    isDeleting,
    fetchMessage,
    saveMessage,
    deleteMessage,
  } = useMessageStore();

  const [content, setContent] = useState('');
  const [isEnabled, setIsEnabled] = useState(true);

  useEffect(() => {
    fetchMessage();
  }, []);

  useEffect(() => {
    if (savedMessageData) {
      setContent(savedMessageData.content || '');
      setIsEnabled(savedMessageData.is_enabled);
    }
  }, [savedMessageData]);

  const hasChanges =
    content !== (savedMessageData?.content || '') ||
    isEnabled !== (savedMessageData?.is_enabled ?? true);

  const handleSave = async () => {
    if (!content.trim()) {
      Alert.alert('알림', '메시지 내용을 입력해주세요.');
      return;
    }

    if (!hasChanges) {
      Alert.alert('알림', '변경된 내용이 없습니다.');
      return;
    }

    try {
      await saveMessage(content, isEnabled);
      Alert.alert('저장 완료', '개인 메시지가 저장되었습니다.');
    } catch {
      Alert.alert('저장 실패', '메시지 저장에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleDelete = () => {
    Alert.alert(
      '메시지 삭제',
      '작성한 메시지를 삭제하시겠습니까?\n삭제된 메시지는 복구할 수 없습니다.',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteMessage();
              setContent('');
              setIsEnabled(false);
              Alert.alert('삭제 완료', '메시지가 삭제되었습니다.');
            } catch {
              Alert.alert('삭제 실패', '메시지 삭제에 실패했습니다.');
            }
          },
        },
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.infoCard}>
            <Ionicons name="information-circle-outline" size={24} color="#007AFF" />
            <Text style={styles.infoText}>
              이 메시지는 체크인이 일정 기간 없을 경우 비상연락처에게 전달됩니다.
              미리 전하고 싶은 말을 작성해주세요.
            </Text>
          </View>

          <View style={styles.toggleContainer}>
            <View style={styles.toggleInfo}>
              <Text style={styles.toggleLabel}>메시지 발송 활성화</Text>
              <Text style={styles.toggleDescription}>
                비활성화하면 상태 알림은 발송되지만 이 메시지는 전달되지 않습니다.
              </Text>
            </View>
            <Switch
              value={isEnabled}
              onValueChange={setIsEnabled}
              trackColor={{ false: '#ddd', true: '#34c759' }}
              thumbColor="#ffffff"
            />
          </View>

          <View style={styles.messageContainer}>
            <View style={styles.messageHeader}>
              <Text style={styles.label}>개인 메시지</Text>
              <Text style={[
                styles.charCount,
                content.length > MAX_MESSAGE_LENGTH * 0.9 && styles.charCountWarning
              ]}>
                {content.length}/{MAX_MESSAGE_LENGTH}
              </Text>
            </View>
            <TextInput
              style={[
                styles.textArea,
                !isEnabled && styles.textAreaDisabled
              ]}
              placeholder="비상연락처에게 전할 메시지를 작성하세요..."
              placeholderTextColor="#999"
              multiline
              maxLength={MAX_MESSAGE_LENGTH}
              value={content}
              onChangeText={setContent}
              textAlignVertical="top"
              editable={!isLoading}
            />
          </View>

          <View style={styles.templateSection}>
            <Text style={styles.templateTitle}>예시 메시지</Text>
            <TouchableOpacity
              style={styles.templateCard}
              onPress={() =>
                setContent(
                  '안녕하세요, 이 메시지를 받으셨다면 제가 오랜 시간 연락이 없었다는 뜻입니다. ' +
                  '걱정되시면 저에게 연락을 시도해주시거나, 직접 확인해주시면 감사하겠습니다.'
                )
              }
            >
              <Text style={styles.templateText}>
                "안녕하세요, 이 메시지를 받으셨다면..."
              </Text>
              <Ionicons name="chevron-forward" size={20} color="#999" />
            </TouchableOpacity>
          </View>
        </ScrollView>

        <View style={styles.bottomActions}>
          {savedMessageData?.id && (
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={handleDelete}
              disabled={isDeleting}
            >
              <Ionicons name="trash-outline" size={20} color="#ff3b30" />
              <Text style={styles.deleteButtonText}>
                {isDeleting ? '삭제 중...' : '삭제'}
              </Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={[
              styles.saveButton,
              (!hasChanges || isSaving || !content.trim()) && styles.saveButtonDisabled,
            ]}
            onPress={handleSave}
            disabled={!hasChanges || isSaving || !content.trim()}
          >
            <Text style={styles.saveButtonText}>
              {isSaving ? '저장 중...' : '저장하기'}
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      <View style={styles.notice}>
        <Text style={styles.noticeText}>
          본 서비스는 사망 여부를 확인하지 않습니다.{'\n'}
          이 메시지는 법적 효력이 없으며, 단순 안부 전달 목적으로만 사용됩니다.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#e8f4ff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    lineHeight: 22,
    marginLeft: 12,
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  toggleInfo: {
    flex: 1,
    marginRight: 16,
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  toggleDescription: {
    fontSize: 12,
    color: '#666',
    lineHeight: 18,
  },
  messageContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  charCount: {
    fontSize: 12,
    color: '#999',
  },
  charCountWarning: {
    color: '#ff9500',
  },
  textArea: {
    minHeight: 200,
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  textAreaDisabled: {
    color: '#999',
    backgroundColor: '#f9f9f9',
  },
  templateSection: {
    marginBottom: 24,
  },
  templateTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 12,
  },
  templateCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  templateText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
  },
  bottomActions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 12,
  },
  deleteButtonText: {
    color: '#ff3b30',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: '#99c9ff',
  },
  saveButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  notice: {
    padding: 16,
    backgroundColor: '#fff9e6',
    borderTopWidth: 1,
    borderTopColor: '#f0e6cc',
  },
  noticeText: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
    lineHeight: 16,
  },
});
