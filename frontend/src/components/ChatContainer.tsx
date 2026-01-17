import React, { useEffect, useRef } from 'react';
import { useBookingStore } from '@/store/bookingStore';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './Loader';

export const ChatContainer: React.FC = () => {
  const { messages, isAgentTyping } = useBookingStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAgentTyping]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <div className="text-6xl mb-4">🚗</div>
            <h3 className="text-xl font-semibold mb-2">Start Your Journey</h3>
            <p className="text-sm">Tell me where you want to go!</p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {isAgentTyping && (
        <div className="flex justify-start mb-4">
          <div className="bg-white rounded-2xl rounded-bl-none shadow-sm border border-gray-200">
            <TypingIndicator />
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
