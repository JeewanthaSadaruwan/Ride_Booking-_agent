// User types
export interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
}

export interface UserStats {
  totalBookings: number;
  completedTrips: number;
  totalSpent: number;
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  name: string;
  email: string;
  phone: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Location types
export interface Location {
  text: string;
  lat: number;
  lon: number;
}

// Route types
export interface Route {
  distance: number; // in km
  duration: number; // in minutes
  polyline: [number, number][]; // array of [lat, lon] coordinates
}

// Vehicle types
export type VehicleType = 'Economy' | 'SUV' | 'Luxury';

export interface Vehicle {
  id: string;
  type: VehicleType;
  name: string;
  capacity: number;
  features: string[];
  pricePerKm: number;
  basePrice: number;
  estimatedPrice?: number;
  eta?: number; // in minutes
  available: boolean;
}

// Booking types
export type BookingStatus = 'confirmed' | 'completed' | 'cancelled' | 'pending';

export interface Booking {
  id: string;
  userId: string;
  pickup: Location;
  dropoff: Location;
  vehicle: Vehicle;
  status: BookingStatus;
  scheduledTime: string;
  estimatedCost: number;
  distance: number;
  duration: number;
  driverName?: string;
  driverPhone?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateBookingRequest {
  pickup: Location;
  dropoff: Location;
  vehicleId: string;
  scheduledTime?: string;
}

// Message types
export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  metadata?: {
    pickup?: Location;
    dropoff?: Location;
    route?: Route;
    vehicles?: Vehicle[];
  };
}

// Chat types
export interface ChatRequest {
  message: string;
  context?: {
    pickup?: Location;
    dropoff?: Location;
  };
}

export interface ChatResponse {
  message: string;
  pickup?: Location;
  dropoff?: Location;
  route?: Route;
  vehicles?: Vehicle[];
  needsMoreInfo?: boolean;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Notification types
export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
}
