import { apiClient, handleApiError } from './api';
import { Booking, CreateBookingRequest, ApiResponse } from '@/types';

export const bookingService = {
  /**
   * Get all bookings for current user
   */
  async getMyBookings(): Promise<Booking[]> {
    try {
      const response = await apiClient.get<ApiResponse<Booking[]>>('/bookings/my');
      return response.data.data || [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create a new booking
   */
  async createBooking(request: CreateBookingRequest): Promise<Booking> {
    try {
      const response = await apiClient.post<ApiResponse<Booking>>('/bookings', request);
      return response.data.data!;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Cancel a booking
   */
  async cancelBooking(bookingId: string): Promise<void> {
    try {
      await apiClient.post(`/bookings/${bookingId}/cancel`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get booking details
   */
  async getBooking(bookingId: string): Promise<Booking> {
    try {
      const response = await apiClient.get<ApiResponse<Booking>>(`/bookings/${bookingId}`);
      return response.data.data!;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
