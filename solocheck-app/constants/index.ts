/**
 * Application Constants
 */

// App Info
export const APP_NAME = 'SoloCheck';
export const APP_VERSION = '1.0.0';

// API
export const API_VERSION = 'v1';
export const DEFAULT_API_TIMEOUT = 10000; // 10 seconds

// Auth
export const TOKEN_KEY = 'auth_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';

// Check-in Settings
export const DEFAULT_CHECKIN_INTERVAL_HOURS = 24;
export const DEFAULT_GRACE_PERIOD_HOURS = 12;
export const MIN_CHECKIN_INTERVAL_HOURS = 6;
export const MAX_CHECKIN_INTERVAL_HOURS = 168; // 7 days

// Check-in Cycles (in days)
export const CHECK_IN_CYCLES = [7, 14, 30] as const;
export type CheckInCycle = (typeof CHECK_IN_CYCLES)[number];

// Grace Periods (in hours)
export const GRACE_PERIODS = [24, 48, 72] as const;
export type GracePeriod = (typeof GRACE_PERIODS)[number];

// Check-in Cycle Labels
export const CHECK_IN_CYCLE_LABELS: Record<CheckInCycle, string> = {
  7: '7일',
  14: '14일',
  30: '30일',
};

// Grace Period Labels
export const GRACE_PERIOD_LABELS: Record<GracePeriod, string> = {
  24: '24시간',
  48: '48시간',
  72: '72시간',
};

// Emergency Contacts
export const MAX_EMERGENCY_CONTACTS = 3;

// Personal Message
export const MAX_MESSAGE_LENGTH = 500;

// Validation
export const PASSWORD_MIN_LENGTH = 6;
export const NAME_MIN_LENGTH = 2;
export const PHONE_REGEX = /^01[0-9]-?[0-9]{4}-?[0-9]{4}$/;

// Colors (Theme) - Warm and calming pastel tones
export const COLORS = {
  // Primary - Warm blue with pastel tone
  primary: '#5B8DEF',
  primaryLight: '#E8F0FF',
  primaryDark: '#3D6BC7',

  // Secondary - Soft purple
  secondary: '#8B7FD6',
  secondaryLight: '#EDE8FF',

  // Status colors - Softer versions
  success: '#4CAF7C',
  successLight: '#E8F5ED',
  warning: '#F5A623',
  warningLight: '#FFF4E0',
  error: '#E57373',
  errorLight: '#FFEBEB',

  // Neutrals - Warm tones
  background: '#F8F9FA',
  surface: '#FFFFFF',
  text: '#2D3436',
  textSecondary: '#636E72',
  textTertiary: '#A0A8AB',
  border: '#E0E4E7',
  borderLight: '#F0F2F4',

  // Specific
  inputBackground: '#F5F6F8',
  disabled: '#B0B8BC',

  // Accent colors for home screen
  checkinButton: '#5B8DEF',
  checkinButtonPressed: '#4A7CDE',
  cardBackground: '#FFFFFF',
  cardShadow: 'rgba(91, 141, 239, 0.15)',
};

// Spacing
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Border Radius
export const BORDER_RADIUS = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
};

// Font Sizes
export const FONT_SIZES = {
  xs: 11,
  sm: 12,
  md: 14,
  lg: 16,
  xl: 18,
  xxl: 20,
  title: 24,
  heading: 28,
  hero: 48,  // Larger for remaining days display
  display: 64, // For big numbers
};

// Legal Notice Text
export const LEGAL_NOTICE = {
  main: '본 서비스는 사망 여부를 확인하지 않습니다.\n긴급 상황 시 112/119 등 공공기관에 연락하세요.\n알림은 \'연락 두절\' 기준으로 발송됩니다.',
  short: '본 서비스는 사망 여부를 확인하지 않습니다.',
  message: '이 메시지는 법적 효력이 없으며, 단순 안부 전달 목적으로만 사용됩니다.',
  contactNotice: '비상연락처로 등록된 분들은 체크인이 일정 기간 없을 경우 알림을 받게 됩니다.',
};
