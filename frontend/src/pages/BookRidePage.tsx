import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useBookingStore } from '@/store/bookingStore';
import { chatService } from '@/services/chatService';
import { locationService } from '@/services/locationService';
import { ChatContainer } from '@/components/ChatContainer';
import { ChatInput } from '@/components/ChatInput';
import { MapComponent } from '@/components/MapComponent';
import { VehicleCard } from '@/components/VehicleCard';
import { BookingConfirmationModal } from '@/components/BookingConfirmationModal';
import { Button } from '@/components/Button';
import { generateId } from '@/utils/helpers';
import toast from 'react-hot-toast';

export const BookRidePage: React.FC = () => {
  const [isMapPicking, setIsMapPicking] = useState(false);
  const [mapPickMode, setMapPickMode] = useState<'pickup' | 'dropoff' | null>(null);
  const [isResolvingPick, setIsResolvingPick] = useState(false);
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
    resetBooking,
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

    // Lightweight map preview for "from X to Y" messages
    if (!pickup && !dropoff) {
      const match = message.match(
        /from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:at|on|tomorrow|today|for|with|by|around|before|after)\b|[.?!]|$)/i
      );
      if (match) {
        const pickupText = match[1].trim();
        const dropoffText = match[2].trim();
        void (async () => {
          try {
            const pickupLocation = await locationService.geocode(pickupText);
            const dropoffLocation = await locationService.geocode(dropoffText);
            setPickup(pickupLocation);
            setDropoff(dropoffLocation);
            const previewRoute = await locationService.calculateRoute(
              pickupLocation,
              dropoffLocation
            );
            setRoute(previewRoute);
          } catch {
            // Ignore map preview errors; agent flow continues normally.
          }
        })();
      }
    }

    // Send to backend
    chatMutation.mutate({
      message,
      context: {
        pickup: pickup || undefined,
        dropoff: dropoff || undefined,
      },
    });
  };

  const handleMapSelect = async (lat: number, lon: number) => {
    if (!mapPickMode) return;
    setIsResolvingPick(true);

    let resolvedText = `Pinned location (${lat.toFixed(5)}, ${lon.toFixed(5)})`;
    try {
      const resolved = await locationService.reverseGeocode(lat, lon);
      resolvedText = resolved.text || resolvedText;
    } catch {
      // Keep fallback text
    }

    const location = {
      text: resolvedText,
      lat,
      lon,
    };

    if (mapPickMode === 'pickup') {
      setPickup(location);
      if (dropoff) {
        try {
          const previewRoute = await locationService.calculateRoute(location, dropoff);
          setRoute(previewRoute);
        } catch {
          // Ignore route errors for map selection
        }
      }
      if (!dropoff) {
        setMapPickMode('dropoff');
      }
    } else {
      setDropoff(location);
      if (pickup) {
        try {
          const previewRoute = await locationService.calculateRoute(pickup, location);
          setRoute(previewRoute);
        } catch {
          // Ignore route errors for map selection
        }
      }
      if (!pickup) {
        setMapPickMode('pickup');
      }
    }

    setIsResolvingPick(false);
  };

  const handleMapDone = () => {
    setIsMapPicking(false);
    setMapPickMode(null);

    if (!pickup && !dropoff) return;
    if (chatMutation.isPending) return;

    const message =
      pickup && dropoff
        ? 'I selected my pickup and dropoff on the map.'
        : pickup
          ? 'I selected my pickup on the map.'
          : 'I selected my dropoff on the map.';

    addMessage({
      id: generateId(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    });

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

  const showVehicles = availableVehicles.length > 0 && route;

  return (
    <div className="flex h-full">
      {/* Left: Chat */}
      <div className="flex-1 flex flex-col bg-gray-50">
        <ChatContainer />
        <ChatInput onSend={handleSendMessage} isLoading={chatMutation.isPending} />
      </div>

      {/* Right: Map and Vehicles */}
      <div className="w-[28rem] border-l border-gray-200 flex flex-col bg-white">
        {/* Map */}
        <div className="h-96 border-b border-gray-200 relative">
          <MapComponent
            pickup={pickup}
            dropoff={dropoff}
            route={route}
            isPicking={isMapPicking}
            onMapSelect={isMapPicking && mapPickMode ? handleMapSelect : undefined}
          />
          {!pickup && !dropoff && !isMapPicking && (
            <div className="absolute inset-0 flex items-center justify-center text-gray-500 pointer-events-none bg-white/70">
              <div className="text-center">
                <div className="text-3xl mb-2">🗺️</div>
                <p className="text-sm">Map is ready. Tell me your pickup and dropoff.</p>
              </div>
            </div>
          )}
        </div>

        <div className="border-b border-gray-200 p-4 space-y-3">
          <div className="text-xs uppercase tracking-wide text-gray-500">Route Preview</div>
          {(pickup || dropoff || route) && !isMapPicking && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                resetBooking();
                setIsMapPicking(false);
                setMapPickMode(null);
              }}
              className="w-full"
            >
              Clear map and chat
            </Button>
          )}
          {!isMapPicking && (!pickup || !dropoff) && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setIsMapPicking(true);
                setMapPickMode(pickup ? 'dropoff' : 'pickup');
              }}
              className="w-full"
            >
              Pick on map
            </Button>
          )}
          {isMapPicking && (
            <div className="space-y-2">
              <div className="text-xs text-gray-500">
                {mapPickMode === 'pickup'
                  ? 'Click on the map to set pickup'
                  : 'Click on the map to set dropoff'}
              </div>
              <div className="flex gap-2">
                <Button
                  variant={mapPickMode === 'pickup' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setMapPickMode('pickup')}
                  className="flex-1"
                >
                  Pick pickup
                </Button>
                <Button
                  variant={mapPickMode === 'dropoff' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setMapPickMode('dropoff')}
                  className="flex-1"
                >
                  Pick dropoff
                </Button>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleMapDone}
                className="w-full"
                disabled={isResolvingPick}
              >
                {isResolvingPick ? 'Resolving location...' : 'Done'}
              </Button>
            </div>
          )}
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
            <div className="text-xs text-gray-500 mb-1">Pickup</div>
            <div className="text-sm font-semibold text-gray-900">
              {pickup?.text || 'Waiting for pickup location'}
            </div>
          </div>
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
            <div className="text-xs text-gray-500 mb-1">Dropoff</div>
            <div className="text-sm font-semibold text-gray-900">
              {dropoff?.text || 'Waiting for dropoff location'}
            </div>
          </div>
          {route && (
            <div className="rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-700">
              <div className="flex items-center justify-between">
                <span>Distance</span>
                <span className="font-semibold">{route.distance.toFixed(1)} km</span>
              </div>
              <div className="flex items-center justify-between mt-1">
                <span>Duration</span>
                <span className="font-semibold">{Math.round(route.duration)} min</span>
              </div>
            </div>
          )}
        </div>

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

        {!showVehicles && <div className="flex-1" />}
      </div>

      {/* Booking Confirmation Modal */}
      <BookingConfirmationModal />
    </div>
  );
};
