import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { Booking } from '@/types';
import { Card } from '@/components/Card';
import { StatusBadge } from '@/components/StatusBadge';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import { formatDateTime, formatPrice, formatDistance, formatDuration } from '@/utils/helpers';
import toast from 'react-hot-toast';

export const MyBookingsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: bookingService.getMyBookings,
  });

  const cancelMutation = useMutation({
    mutationFn: bookingService.cancelBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] });
      toast.success('Booking cancelled successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to cancel booking');
    },
  });

  const handleCancelBooking = (bookingId: string) => {
    if (confirm('Are you sure you want to cancel this booking?')) {
      cancelMutation.mutate(bookingId);
    }
  };

  const toggleExpand = (bookingId: string) => {
    setExpandedId(expandedId === bookingId ? null : bookingId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader />
      </div>
    );
  }

  if (bookings.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold mb-2">No Bookings Yet</h3>
          <p className="text-sm">Start booking your first ride!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <h2 className="text-2xl font-bold mb-6">My Bookings</h2>

      <div className="space-y-4 max-w-4xl">
        {bookings.map((booking) => (
          <BookingCard
            key={booking.id}
            booking={booking}
            isExpanded={expandedId === booking.id}
            onToggle={() => toggleExpand(booking.id)}
            onCancel={handleCancelBooking}
            isCancelling={cancelMutation.isPending}
          />
        ))}
      </div>
    </div>
  );
};

interface BookingCardProps {
  booking: Booking;
  isExpanded: boolean;
  onToggle: () => void;
  onCancel: (id: string) => void;
  isCancelling: boolean;
}

const BookingCard: React.FC<BookingCardProps> = ({
  booking,
  isExpanded,
  onToggle,
  onCancel,
  isCancelling,
}) => {
  const canCancel = booking.status === 'confirmed' || booking.status === 'pending';
  const pickupText = booking.pickup?.text || 'Unknown pickup';
  const dropoffText = booking.dropoff?.text || 'Unknown dropoff';
  const vehicleName = booking.vehicle?.name || 'Unknown vehicle';
  const vehicleType = booking.vehicle?.type || 'Unknown';

  return (
    <Card className="cursor-pointer" onClick={onToggle}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-bold text-lg">Booking #{booking.id.slice(0, 8)}</h3>
            <StatusBadge status={booking.status} />
          </div>
          <div className="text-sm text-gray-600">
            {formatDateTime(booking.scheduledTime)}
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary-600">
            {formatPrice(booking.estimatedCost)}
          </div>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-start gap-2">
          <span className="text-green-600 font-bold">A</span>
          <div className="flex-1">
            <div className="text-gray-600">From</div>
            <div className="font-medium">{pickupText}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-red-600 font-bold">B</span>
          <div className="flex-1">
            <div className="text-gray-600">To</div>
            <div className="font-medium">{dropoffText}</div>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-600">Vehicle</div>
              <div className="font-medium">{vehicleName}</div>
              <div className="text-sm text-gray-600">{vehicleType}</div>
            </div>
            <div>
              <div className="text-xs text-gray-600">Distance & Duration</div>
              <div className="font-medium">{formatDistance(booking.distance)}</div>
              <div className="text-sm text-gray-600">{formatDuration(booking.duration)}</div>
            </div>
          </div>

          {booking.driverName && (
            <div>
              <div className="text-xs text-gray-600">Driver</div>
              <div className="font-medium">{booking.driverName}</div>
              {booking.driverPhone && (
                <div className="text-sm text-gray-600">📞 {booking.driverPhone}</div>
              )}
            </div>
          )}

          {canCancel && (
            <div className="pt-2">
              <Button
                variant="danger"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onCancel(booking.id);
                }}
                isLoading={isCancelling}
                className="w-full"
              >
                Cancel Booking
              </Button>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};
