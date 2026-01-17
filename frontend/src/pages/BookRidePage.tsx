import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useBookingStore } from '@/store/bookingStore';
import { chatService } from '@/services/chatService';
import { ChatContainer } from '@/components/ChatContainer';
import { ChatInput } from '@/components/ChatInput';
import { MapComponent } from '@/components/MapComponent';
import { VehicleCard } from '@/components/VehicleCard';
import { BookingConfirmationModal } from '@/components/BookingConfirmationModal';
import { Button } from '@/components/Button';
import { generateId } from '@/utils/helpers';
import toast from 'react-hot-toast';

export const BookRidePage: React.FC = () => {
  const {
    addMessage,
    setAgentTyping,
    pickup,
    dropoff,
    route,
    availableVehicles,
    selectedVehicle,
    setPickup,
    setDropoff,
    setRoute,
    setAvailableVehicles,
    setSelectedVehicle,
    setShowConfirmationModal,
  } = useBookingStore();

  const chatMutation = useMutation({
    mutationFn: chatService.sendMessage,
    onMutate: () => {
      setAgentTyping(true);
    },
    onSuccess: (response) => {
      setAgentTyping(false);

      // Add agent response
      addMessage({
        id: generateId(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      });

      // Update locations if detected
      if (response.pickup && (!pickup || response.pickup.text !== pickup.text)) {
        setPickup(response.pickup);
        addMessage({
          id: generateId(),
          role: 'system',
          content: `✓ Pickup location identified: ${response.pickup.text}`,
          timestamp: new Date(),
        });
      }

      if (response.dropoff && (!dropoff || response.dropoff.text !== dropoff.text)) {
        setDropoff(response.dropoff);
        addMessage({
          id: generateId(),
          role: 'system',
          content: `✓ Dropoff location identified: ${response.dropoff.text}`,
          timestamp: new Date(),
        });
      }

      // Update route if calculated
      if (response.route) {
        setRoute(response.route);
        addMessage({
          id: generateId(),
          role: 'system',
          content: `✓ Route calculated: ${response.route.distance.toFixed(1)} km, ${Math.round(response.route.duration)} minutes`,
          timestamp: new Date(),
        });
      }

      // Update vehicles if available
      if (response.vehicles && response.vehicles.length > 0) {
        setAvailableVehicles(response.vehicles);
      }
    },
    onError: (error: Error) => {
      setAgentTyping(false);
      toast.error(error.message || 'Failed to send message');
    },
  });

  const handleSendMessage = (message: string) => {
    // Add user message
    addMessage({
      id: generateId(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    });

    // Send to backend
    chatMutation.mutate({
      message,
      context: {
        pickup: pickup || undefined,
        dropoff: dropoff || undefined,
      },
    });
  };

  const handleVehicleSelect = (vehicle: typeof availableVehicles[0]) => {
    setSelectedVehicle(vehicle);
  };

  const handleProceedToBooking = () => {
    if (!selectedVehicle) {
      toast.error('Please select a vehicle');
      return;
    }
    setShowConfirmationModal(true);
  };

  const showMap = pickup || dropoff;
  const showVehicles = availableVehicles.length > 0 && route;

  return (
    <div className="flex h-full">
      {/* Left: Chat */}
      <div className="flex-1 flex flex-col bg-gray-50">
        <ChatContainer />
        <ChatInput onSend={handleSendMessage} isLoading={chatMutation.isPending} />
      </div>

      {/* Right: Map and Vehicles */}
      <div className="w-96 border-l border-gray-200 flex flex-col bg-white">
        {/* Map */}
        {showMap && (
          <div className="h-64 border-b border-gray-200">
            <MapComponent
              pickup={pickup}
              dropoff={dropoff}
              route={route}
            />
          </div>
        )}

        {/* Vehicle Selection */}
        {showVehicles && (
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="font-bold text-lg mb-4">Select Vehicle</h3>
            <div className="space-y-3">
              {availableVehicles.map((vehicle) => (
                <VehicleCard
                  key={vehicle.id}
                  vehicle={vehicle}
                  isSelected={selectedVehicle?.id === vehicle.id}
                  onSelect={() => handleVehicleSelect(vehicle)}
                />
              ))}
            </div>

            {selectedVehicle && (
              <div className="mt-4 sticky bottom-0 bg-white pt-4 border-t">
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full"
                  onClick={handleProceedToBooking}
                >
                  Continue to Booking
                </Button>
              </div>
            )}
          </div>
        )}

        {!showMap && !showVehicles && (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-6xl mb-4">🗺️</div>
              <p className="text-sm">Map will appear here</p>
            </div>
          </div>
        )}
      </div>

      {/* Booking Confirmation Modal */}
      <BookingConfirmationModal />
    </div>
  );
};
