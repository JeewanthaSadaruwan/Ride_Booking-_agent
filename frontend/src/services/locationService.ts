import { apiClient, handleApiError } from './api';
import { Location, Route, Vehicle, ApiResponse } from '@/types';

export const locationService = {
  /**
   * Geocode location text to coordinates
   */
  async geocode(locationText: string): Promise<Location> {
    try {
      const response = await apiClient.post<ApiResponse<Location>>('/location/geocode', {
        location: locationText,
      });
      return response.data.data!;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Calculate route between two locations
   */
  async calculateRoute(pickup: Location, dropoff: Location): Promise<Route> {
    try {
      const response = await apiClient.post<ApiResponse<Route>>('/location/route', {
        pickup,
        dropoff,
      });
      return response.data.data!;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

export const vehicleService = {
  /**
   * Get available vehicles
   */
  async getAvailableVehicles(): Promise<Vehicle[]> {
    try {
      const response = await apiClient.get<ApiResponse<Vehicle[]>>('/vehicles');
      return response.data.data || [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get vehicle recommendations based on route
   */
  async getRecommendations(distance: number): Promise<Vehicle[]> {
    try {
      const response = await apiClient.post<ApiResponse<Vehicle[]>>('/vehicles/recommend', {
        distance,
      });
      return response.data.data || [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
