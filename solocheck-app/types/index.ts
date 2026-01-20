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
export interface EmergencyContact {
  id: string;
  userId: string;
  name: string;
  phone: string;
  email?: string;
  relationship?: string;
  isVerified: boolean;
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
