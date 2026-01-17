import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { BookRidePage } from '@/pages/BookRidePage';
import { MyBookingsPage } from '@/pages/MyBookingsPage';

export const Layout: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'book' | 'bookings'>('book');

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar with Tabs */}
        <div className="bg-white border-b border-gray-200 shadow-sm">
          <div className="flex">
            <button
              onClick={() => setActiveTab('book')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'book'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              💬 Book a Ride
            </button>
            <button
              onClick={() => setActiveTab('bookings')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'bookings'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📋 My Bookings
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'book' ? <BookRidePage /> : <MyBookingsPage />}
        </div>
      </div>
    </div>
  );
};
