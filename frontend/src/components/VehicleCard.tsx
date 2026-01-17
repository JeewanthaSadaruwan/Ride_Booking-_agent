import React from 'react';
import { Vehicle } from '@/types';
import { formatPrice } from '@/utils/helpers';
import { Card } from './Card';
import { cn } from '@/utils/helpers';

interface VehicleCardProps {
  vehicle: Vehicle;
  isSelected: boolean;
  onSelect: () => void;
}

export const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, isSelected, onSelect }) => {
  const vehicleEmoji = {
    Economy: '🚗',
    SUV: '🚙',
    Luxury: '🚘',
  };

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all',
        isSelected ? 'ring-2 ring-primary-500 shadow-lg' : 'hover:shadow-lg'
      )}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-3xl">{vehicleEmoji[vehicle.type]}</span>
            <div>
              <h3 className="font-bold text-lg">{vehicle.name}</h3>
              <p className="text-sm text-gray-600">{vehicle.type}</p>
            </div>
          </div>

          <div className="space-y-1 mb-3">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>👥</span>
              <span>Up to {vehicle.capacity} passengers</span>
            </div>
            {vehicle.features.slice(0, 2).map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                <span>✓</span>
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="text-right">
          {vehicle.estimatedPrice && (
            <div className="text-2xl font-bold text-primary-600">
              {formatPrice(vehicle.estimatedPrice)}
            </div>
          )}
          {vehicle.eta && (
            <div className="text-sm text-gray-600 mt-1">
              ETA: {vehicle.eta} min
            </div>
          )}
        </div>
      </div>

      <button
        className={cn(
          'w-full mt-4 py-2 rounded-lg font-semibold transition-colors',
          isSelected
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        )}
      >
        {isSelected ? '✓ Selected' : 'Select'}
      </button>
    </Card>
  );
};
