import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { useBookingStore } from '@/store/bookingStore';
import { bookingService } from '@/services/bookingService';
import { Button } from './Button';

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore();
  const { resetBooking } = useBookingStore();

  // Fetch user's bookings for stats
  const { data: bookings = [] } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: bookingService.getMyBookings,
  });

  const completedTrips = bookings.filter(b => b.status === 'completed').length;

  const handleNewTrip = () => {
    resetBooking();
  };

  return (
    <div className="w-80 bg-gradient-to-b from-primary-600 to-primary-800 text-white h-screen flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-primary-500">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          🚗 Ride Booking Agent
        </h1>
      </div>

      {/* User Profile */}
      {user && (
        <div className="p-6 bg-primary-700 bg-opacity-50">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-primary-400 rounded-full flex items-center justify-center text-xl font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 overflow-hidden">
              <h3 className="font-semibold text-lg truncate">{user.name}</h3>
              <p className="text-sm text-primary-200 truncate">{user.email}</p>
            </div>
          </div>
          <p className="text-sm text-primary-200">📞 {user.phone}</p>
        </div>
      )}

      {/* Stats */}
      <div className="p-6 space-y-3">
        <div className="bg-primary-700 bg-opacity-50 rounded-lg p-4">
          <div className="text-2xl font-bold">{bookings.length}</div>
          <div className="text-sm text-primary-200">Total Bookings</div>
        </div>
        <div className="bg-primary-700 bg-opacity-50 rounded-lg p-4">
          <div className="text-2xl font-bold">{completedTrips}</div>
          <div className="text-sm text-primary-200">Completed Trips</div>
        </div>
      </div>

      {/* New Trip Button */}
      <div className="px-6 mb-6">
        <Button
          onClick={handleNewTrip}
          className="w-full bg-white text-primary-600 hover:bg-primary-50"
        >
          ✨ Start New Trip
        </Button>
      </div>

      {/* Navigation - would be tabs in main area */}
      <div className="px-6 space-y-2 flex-1">
        <div className="text-sm font-semibold text-primary-200 mb-2">NAVIGATION</div>
        {/* Navigation handled by tabs in main area */}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-primary-500 text-sm">
        <div className="space-y-2 text-primary-200">
          <div>✓ Real-time booking</div>
          <div>✓ Multiple vehicle types</div>
          <div>✓ AI-powered agent</div>
          <div className="pt-3 text-xs">v1.0.0</div>
        </div>
      </div>
    </div>
  );
};
