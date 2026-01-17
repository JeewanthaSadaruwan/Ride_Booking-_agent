import { create } from 'zustand';
import { Message, Location, Route, Vehicle } from '@/types';

interface BookingState {
  // Chat state
  messages: Message[];
  isAgentTyping: boolean;
  
  // Location state
  pickup: Location | null;
  dropoff: Location | null;
  
  // Route state
  route: Route | null;
  
  // Vehicle state
  availableVehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  
  // Booking confirmation state
  showConfirmationModal: boolean;
  
  // Actions
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  setAgentTyping: (isTyping: boolean) => void;
  setPickup: (location: Location | null) => void;
  setDropoff: (location: Location | null) => void;
  setRoute: (route: Route | null) => void;
  setAvailableVehicles: (vehicles: Vehicle[]) => void;
  setSelectedVehicle: (vehicle: Vehicle | null) => void;
  setShowConfirmationModal: (show: boolean) => void;
  resetBooking: () => void;
}

export const useBookingStore = create<BookingState>((set) => ({
  messages: [],
  isAgentTyping: false,
  pickup: null,
  dropoff: null,
  route: null,
  availableVehicles: [],
  selectedVehicle: null,
  showConfirmationModal: false,
  
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  
  setMessages: (messages) => set({ messages }),
  
  setAgentTyping: (isTyping) => set({ isAgentTyping: isTyping }),
  
  setPickup: (location) => set({ pickup: location }),
  
  setDropoff: (location) => set({ dropoff: location }),
  
  setRoute: (route) => set({ route }),
  
  setAvailableVehicles: (vehicles) => set({ availableVehicles: vehicles }),
  
  setSelectedVehicle: (vehicle) => set({ selectedVehicle: vehicle }),
  
  setShowConfirmationModal: (show) => set({ showConfirmationModal: show }),
  
  resetBooking: () => set({
    messages: [],
    isAgentTyping: false,
    pickup: null,
    dropoff: null,
    route: null,
    availableVehicles: [],
    selectedVehicle: null,
    showConfirmationModal: false,
  }),
}));
