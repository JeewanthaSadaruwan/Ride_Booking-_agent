import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBookingStore } from '@/store/bookingStore';
import { bookingService } from '@/services/bookingService';
import { Modal } from './Modal';
import { Button } from './Button';
import { formatPrice, formatDistance, formatDuration } from '@/utils/helpers';
import toast from 'react-hot-toast';

export const BookingConfirmationModal: React.FC = () => {
  const queryClient = useQueryClient();
  const {
    showConfirmationModal,
    setShowConfirmationModal,
    pickup,
    dropoff,
    route,
    selectedVehicle,
    resetBooking,
  } = useBookingStore();

  const createBookingMutation = useMutation({
    mutationFn: bookingService.createBooking,
    onSuccess: (booking) => {
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] });
      setShowConfirmationModal(false);
      toast.success('Booking confirmed! 🎉');
      
      // Show booking details
      setTimeout(() => {
        toast.success(
          `Booking ID: ${booking.id}\nDriver will arrive soon!`,
          { duration: 5000 }
        );
      }, 500);

      // Reset for new booking
      resetBooking();
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create booking');
    },
  });

  const handleConfirm = () => {
    if (!pickup || !dropoff || !selectedVehicle) return;

    createBookingMutation.mutate({
      pickup,
      dropoff,
      vehicleId: selectedVehicle.id,
    });
  };

  if (!pickup || !dropoff || !selectedVehicle || !route) return null;

  const estimatedCost = selectedVehicle.estimatedPrice || 
    (selectedVehicle.basePrice + route.distance * selectedVehicle.pricePerKm);

  return (
    <Modal
      isOpen={showConfirmationModal}
      onClose={() => setShowConfirmationModal(false)}
      title="Confirm Your Booking"
    >
      <div className="space-y-4">
        {/* Trip Details */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold mb-3">Trip Details</h4>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold">A</span>
              <div className="flex-1">
                <div className="text-gray-600">Pickup</div>
                <div className="font-medium">{pickup.text}</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-red-600 font-bold">B</span>
              <div className="flex-1">
                <div className="text-gray-600">Dropoff</div>
                <div className="font-medium">{dropoff.text}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Route Info */}
        <div className="flex gap-4 text-center">
          <div className="flex-1 bg-blue-50 rounded-lg p-3">
            <div className="text-sm text-gray-600">Distance</div>
            <div className="font-bold text-lg">{formatDistance(route.distance)}</div>
          </div>
          <div className="flex-1 bg-blue-50 rounded-lg p-3">
            <div className="text-sm text-gray-600">Duration</div>
            <div className="font-bold text-lg">{formatDuration(route.duration)}</div>
          </div>
        </div>

        {/* Vehicle Details */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold mb-2">Vehicle</h4>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">{selectedVehicle.name}</div>
              <div className="text-sm text-gray-600">{selectedVehicle.type}</div>
            </div>
            <div className="text-2xl font-bold text-primary-600">
              {formatPrice(estimatedCost)}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            variant="outline"
            size="lg"
            className="flex-1"
            onClick={() => setShowConfirmationModal(false)}
            disabled={createBookingMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="lg"
            className="flex-1"
            onClick={handleConfirm}
            isLoading={createBookingMutation.isPending}
          >
            Confirm Booking
          </Button>
        </div>
      </div>
    </Modal>
  );
};
