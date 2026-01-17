import { format, formatDistance } from 'date-fns';

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date): string => {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) {
    return '-';
  }
  return format(parsed, 'MMM d, yyyy');
};

/**
 * Format time to readable string
 */
export const formatTime = (date: string | Date): string => {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) {
    return '-';
  }
  return format(parsed, 'h:mm a');
};

/**
 * Format date and time
 */
export const formatDateTime = (date: string | Date): string => {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) {
    return '-';
  }
  return format(parsed, 'MMM d, yyyy h:mm a');
};

/**
 * Get relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) {
    return '-';
  }
  return formatDistance(parsed, new Date(), { addSuffix: true });
};

/**
 * Format duration in minutes to readable string
 */
export const formatDuration = (minutes: number): string => {
  if (!Number.isFinite(minutes)) {
    return '-';
  }
  if (minutes < 60) {
    return `${Math.round(minutes)} min`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
};

/**
 * Format distance in km
 */
export const formatDistance = (km: number): string => {
  if (!Number.isFinite(km)) {
    return '-';
  }
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  }
  return `${km.toFixed(1)} km`;
};

/**
 * Format price in currency
 */
export const formatPrice = (amount: number): string => {
  if (!Number.isFinite(amount)) {
    return 'LKR -';
  }
  return `LKR ${amount.toFixed(2)}`;
};

/**
 * Generate unique ID
 */
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Combine class names
 */
export const cn = (...classes: (string | boolean | undefined)[]): string => {
  return classes.filter(Boolean).join(' ');
};
