import React, { useState } from 'react';
import { Button } from './Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="I want to go from Colombo to Kandy..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          disabled={isLoading}
        />
        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={!message.trim() || isLoading}
          isLoading={isLoading}
        >
          Send
        </Button>
      </div>
      <div className="mt-2 text-xs text-gray-500">
        Example: "I need a ride from Colombo Fort to Galle Face at 3 PM"
      </div>
    </form>
  );
};
