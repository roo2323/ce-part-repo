// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
  createdAt: string;
  updatedAt: string;
  checkInIntervalHours?: number;
  gracePeriodHours?: number;
  personalMessage?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  phone: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

// Check-in Types
export interface CheckIn {
  id: string;
  userId: string;
  checkedAt: string;
  createdAt: string;
}

export interface CheckInResponse {
  checkin: CheckIn;
  message: string;
}

export interface CheckInHistoryResponse {
  checkins: CheckIn[];
  total: number;
  page: number;
  limit: number;
}

// Emergency Contact Types
export type ConsentStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export interface EmergencyContact {
  id: string;
  userId: string;
  name: string;
  phone: string;
  email?: string;
  relationship?: string;
  isVerified: boolean;
  status: ConsentStatus;
  consentRequestedAt?: string;
  consentRespondedAt?: string;
  consentExpiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateContactRequest {
  name: string;
  phone: string;
  email?: string;
  relationship?: string;
}

export interface UpdateContactRequest {
  name?: string;
  phone?: string;
  email?: string;
  relationship?: string;
}

// Notification Types
export interface Notification {
  id: string;
  userId: string;
  type: 'checkin_reminder' | 'contact_alert' | 'system';
  title: string;
  body: string;
  isRead: boolean;
  createdAt: string;
}

// Settings Types
export interface UserSettings {
  checkInIntervalHours: number;
  gracePeriodHours: number;
  notificationsEnabled: boolean;
  reminderEnabled: boolean;
  reminderTime?: string;
}

// Reminder Settings Types
export interface ReminderSettings {
  id: string;
  userId: string;
  reminderHoursBefore: number[];
  quietHoursStart: string | null;
  quietHoursEnd: string | null;
  preferredTime: string | null;
  pushEnabled: boolean;
  emailEnabled: boolean;
  customMessage: string | null;
}

export interface UpdateReminderSettingsRequest {
  reminder_hours_before?: number[];
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  preferred_time?: string | null;
  push_enabled?: boolean;
  email_enabled?: boolean;
  custom_message?: string | null;
}

// Quick Check-in Types
export interface QuickCheckInRequest {
  token: string;
  device_type?: 'push' | 'widget';
}

export interface QuickCheckInResponse {
  success: boolean;
  id?: string;
  checked_at?: string;
  next_check_in_due?: string;
  message: string;
}

// Deep Link Types
export interface DeepLinkParams {
  auto?: string;
  token?: string;
}

// SOS Types
export type SOSStatus = 'triggered' | 'cancelled' | 'sent';

export interface SOSEvent {
  id: string;
  userId: string;
  triggeredAt: string;
  cancelledAt?: string;
  sentAt?: string;
  locationLat?: number;
  locationLng?: number;
  status: SOSStatus;
  createdAt: string;
}

export interface SOSTriggerRequest {
  location_lat?: number;
  location_lng?: number;
}

export interface SOSTriggerResponse {
  message: string;
  event: SOSEvent;
  countdown_seconds: number;
}

export interface SOSCancelResponse {
  message: string;
  event: SOSEvent;
}

// Pet Types
export type PetSpecies = 'dog' | 'cat' | 'bird' | 'fish' | 'reptile' | 'small_animal' | 'other';

export interface Pet {
  id: string;
  userId: string;
  name: string;
  species: PetSpecies;
  breed?: string;
  birthDate?: string;
  weight?: number;
  medicalNotes?: string;
  vetInfo?: string;
  caretakerContact?: string;
  photoUrl?: string;
  includeInAlert: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreatePetRequest {
  name: string;
  species: PetSpecies;
  breed?: string;
  birth_date?: string;
  weight?: number;
  medical_notes?: string;
  vet_info?: string;
  caretaker_contact?: string;
  photo_url?: string;
  include_in_alert?: boolean;
}

export interface UpdatePetRequest {
  name?: string;
  species?: PetSpecies;
  breed?: string;
  birth_date?: string;
  weight?: number;
  medical_notes?: string;
  vet_info?: string;
  caretaker_contact?: string;
  photo_url?: string;
  include_in_alert?: boolean;
}

export interface PetListResponse {
  pets: Pet[];
  total: number;
}

// Vault Types
export type VaultCategory = 'medical' | 'housing' | 'insurance' | 'financial' | 'other';

export interface VaultItem {
  id: string;
  userId: string;
  category: VaultCategory;
  title: string;
  content?: string;
  includeInAlert: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateVaultRequest {
  category: VaultCategory;
  title: string;
  content: string;
  include_in_alert?: boolean;
}

export interface UpdateVaultRequest {
  category?: VaultCategory;
  title?: string;
  content?: string;
  include_in_alert?: boolean;
}

export interface VaultListResponse {
  items: VaultItem[];
  total: number;
}

// Location Types
export interface LocationConsent {
  locationConsent: boolean;
  locationConsentAt: string | null;
}

export interface LocationConsentResponse {
  location_consent: boolean;
  location_consent_at: string | null;
  message: string;
}

export interface LocationSharingLog {
  id: string;
  userId: string;
  eventType: 'sos' | 'missed_checkin';
  locationLat: number | null;
  locationLng: number | null;
  recipientIds: string[] | null;
  sharedAt: string;
  createdAt: string;
}

export interface LocationSharingHistoryResponse {
  logs: LocationSharingLog[];
  total: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}
