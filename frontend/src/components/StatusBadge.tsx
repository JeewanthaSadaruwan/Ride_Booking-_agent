import React from 'react';
import { BookingStatus } from '@/types';
import { cn } from '@/utils/helpers';

interface BadgeProps {
  status: BookingStatus;
}

export const StatusBadge: React.FC<BadgeProps> = ({ status }) => {
  const variants = {
    confirmed: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    pending: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={cn(
      'px-3 py-1 rounded-full text-xs font-semibold uppercase',
      variants[status]
    )}>
      {status}
    </span>
  );
};
