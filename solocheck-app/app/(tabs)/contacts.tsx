import { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { contactsService } from '@/services/contacts.service';
import ConsentBadge from '@/components/contacts/ConsentBadge';
import type { EmergencyContact } from '@/types';

const MAX_CONTACTS = 3;

const contactSchema = z.object({
  name: z.string().min(1, '이름을 입력하세요'),
  phone: z.string().regex(/^01[0-9]-?[0-9]{4}-?[0-9]{4}$/, '올바른 전화번호 형식이 아닙니다'),
  email: z.string().email('올바른 이메일 형식이 아닙니다').optional().or(z.literal('')),
  relationship: z.string().optional(),
});

type ContactFormData = z.infer<typeof contactSchema>;

export default function ContactsScreen() {
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingContact, setEditingContact] = useState<EmergencyContact | null>(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: '',
      phone: '',
      email: '',
      relationship: '',
    },
  });

  const fetchContacts = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await contactsService.getContacts();
      setContacts(data);
    } catch (error) {
      Alert.alert('오류', '연락처를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

  const openAddModal = () => {
    if (contacts.length >= MAX_CONTACTS) {
      Alert.alert('알림', `비상연락처는 최대 ${MAX_CONTACTS}명까지 등록할 수 있습니다.`);
      return;
    }
    setEditingContact(null);
    reset({
      name: '',
      phone: '',
      email: '',
      relationship: '',
    });
    setIsModalVisible(true);
  };

  const openEditModal = (contact: EmergencyContact) => {
    setEditingContact(contact);
    reset({
      name: contact.name,
      phone: contact.phone,
      email: contact.email || '',
      relationship: contact.relationship || '',
    });
    setIsModalVisible(true);
  };

  const closeModal = () => {
    setIsModalVisible(false);
    setEditingContact(null);
    reset();
  };

  const onSubmit = async (data: ContactFormData) => {
    try {
      if (editingContact) {
        await contactsService.updateContact(editingContact.id, data);
        Alert.alert('완료', '연락처가 수정되었습니다.');
      } else {
        await contactsService.createContact(data);
        Alert.alert('완료', '연락처가 추가되었습니다.');
      }
      closeModal();
      fetchContacts();
    } catch (error) {
      Alert.alert('오류', '연락처 저장에 실패했습니다.');
    }
  };

  const handleDelete = (contact: EmergencyContact) => {
    Alert.alert(
      '연락처 삭제',
      `${contact.name}님을 비상연락처에서 삭제하시겠습니까?`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              await contactsService.deleteContact(contact.id);
              fetchContacts();
            } catch (error) {
              Alert.alert('오류', '삭제에 실패했습니다.');
            }
          },
        },
      ]
    );
  };

  const handleRequestConsent = async (contact: EmergencyContact) => {
    Alert.alert(
      '동의 요청',
      `${contact.name}님에게 비상연락처 동의 요청을 보내시겠습니까?\n\n동의 요청은 이메일로 발송되며, 7일간 유효합니다.`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '요청 보내기',
          onPress: async () => {
            try {
              const result = await contactsService.requestConsent(contact.id);
              Alert.alert('완료', result.message);
              fetchContacts();
            } catch (error) {
              Alert.alert('오류', '동의 요청 발송에 실패했습니다.');
            }
          },
        },
      ]
    );
  };

  const renderContact = ({ item }: { item: EmergencyContact }) => (
    <View style={styles.contactCard}>
      <View style={styles.contactInfo}>
        <View style={styles.contactAvatar}>
          <Ionicons name="person" size={24} color="#007AFF" />
        </View>
        <View style={styles.contactDetails}>
          <View style={styles.contactNameRow}>
            <Text style={styles.contactName}>{item.name}</Text>
            <ConsentBadge status={item.status} />
          </View>
          <Text style={styles.contactPhone}>{item.phone || item.email}</Text>
          {item.relationship && (
            <Text style={styles.contactRelationship}>{item.relationship}</Text>
          )}
        </View>
      </View>
      <View style={styles.contactActions}>
        {(item.status === 'pending' || item.status === 'expired' || item.status === 'rejected') && (
          <TouchableOpacity
            style={[styles.actionButton, styles.consentButton]}
            onPress={() => handleRequestConsent(item)}
          >
            <Ionicons name="paper-plane-outline" size={18} color="#007AFF" />
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => openEditModal(item)}
        >
          <Ionicons name="pencil" size={20} color="#666" />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleDelete(item)}
        >
          <Ionicons name="trash-outline" size={20} color="#ff3b30" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <View style={styles.header}>
        <Text style={styles.headerText}>
          비상연락처 ({contacts.length}/{MAX_CONTACTS})
        </Text>
        <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
          <Ionicons name="add" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {contacts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="people-outline" size={64} color="#ccc" />
          <Text style={styles.emptyText}>등록된 비상연락처가 없습니다</Text>
          <Text style={styles.emptySubtext}>
            비상시 알림을 받을 연락처를 추가해주세요
          </Text>
          <TouchableOpacity style={styles.emptyAddButton} onPress={openAddModal}>
            <Text style={styles.emptyAddButtonText}>연락처 추가</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={contacts}
          renderItem={renderContact}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          refreshing={isLoading}
          onRefresh={fetchContacts}
        />
      )}

      <View style={styles.notice}>
        <Text style={styles.noticeText}>
          비상연락처로 등록된 분들은 체크인이 일정 기간 없을 경우 알림을 받게 됩니다.
        </Text>
      </View>

      <Modal
        visible={isModalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={closeModal}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={closeModal}>
              <Text style={styles.modalCancel}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>
              {editingContact ? '연락처 수정' : '연락처 추가'}
            </Text>
            <TouchableOpacity onPress={handleSubmit(onSubmit)}>
              <Text style={styles.modalSave}>저장</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.modalContent}>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>이름 *</Text>
              <Controller
                control={control}
                name="name"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.name && styles.inputError]}
                    placeholder="이름을 입력하세요"
                    placeholderTextColor="#999"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                  />
                )}
              />
              {errors.name && <Text style={styles.errorText}>{errors.name.message}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>전화번호 *</Text>
              <Controller
                control={control}
                name="phone"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.phone && styles.inputError]}
                    placeholder="010-0000-0000"
                    placeholderTextColor="#999"
                    keyboardType="phone-pad"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                  />
                )}
              />
              {errors.phone && <Text style={styles.errorText}>{errors.phone.message}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>이메일</Text>
              <Controller
                control={control}
                name="email"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.email && styles.inputError]}
                    placeholder="이메일 (선택)"
                    placeholderTextColor="#999"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                  />
                )}
              />
              {errors.email && <Text style={styles.errorText}>{errors.email.message}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>관계</Text>
              <Controller
                control={control}
                name="relationship"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={styles.input}
                    placeholder="예: 부모님, 친구, 형제 등"
                    placeholderTextColor="#999"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                  />
                )}
              />
            </View>
          </View>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  addButton: {
    padding: 8,
  },
  listContent: {
    padding: 16,
  },
  contactCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  contactInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  contactAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#e8f4ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contactDetails: {
    flex: 1,
  },
  contactNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  contactName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  verifiedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    gap: 2,
  },
  verifiedBadgeActive: {
    backgroundColor: '#e8f8ec',
  },
  verifiedBadgePending: {
    backgroundColor: '#fff5e6',
  },
  verifiedBadgeText: {
    fontSize: 10,
    fontWeight: '500',
  },
  verifiedText: {
    color: '#34c759',
  },
  pendingText: {
    color: '#ff9500',
  },
  contactPhone: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  contactRelationship: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  contactActions: {
    flexDirection: 'row',
  },
  actionButton: {
    padding: 8,
    marginLeft: 8,
  },
  consentButton: {
    backgroundColor: '#e8f4ff',
    borderRadius: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 48,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  emptyAddButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    marginTop: 24,
  },
  emptyAddButtonText: {
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
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    lineHeight: 18,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalCancel: {
    fontSize: 16,
    color: '#666',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  modalSave: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  modalContent: {
    padding: 24,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    backgroundColor: '#ffffff',
  },
  inputError: {
    borderColor: '#ff3b30',
  },
  errorText: {
    color: '#ff3b30',
    fontSize: 12,
    marginTop: 4,
  },
});
