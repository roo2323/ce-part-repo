// API Error Types
export interface ApiError {
  statusCode: number;
  message: string;
  error: string;
}

// API Request/Response Types
export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  data?: unknown;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Auth Request Types
export interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Auth Response Types
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterResponse extends TokenResponse {
  id: string;
  email: string;
  nickname?: string;
}

export interface LoginResponse extends TokenResponse {
  user: {
    id: string;
    email: string;
    nickname?: string;
  };
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

// User API Types
export interface UpdateUserRequest {
  name?: string;
  phone?: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface UpdateMessageRequest {
  message: string;
}

// Check-in API Types
export interface CheckInCreateResponse {
  checkin: {
    id: string;
    userId: string;
    checkedAt: string;
    createdAt: string;
  };
  message: string;
}

export interface CheckInStatusResponse {
  lastCheckIn: {
    id: string;
    checkedAt: string;
  } | null;
  hoursSinceLastCheckIn: number | null;
  isOverdue: boolean;
}

// Contact API Types
export interface CreateContactResponse {
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

export interface TestNotificationResponse {
  success: boolean;
  message: string;
}
