import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message as MessageType } from '@/types';
import { formatTime } from '@/utils/helpers';
import { cn } from '@/utils/helpers';

interface ChatMessageProps {
  message: MessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg text-sm max-w-md text-center">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('flex mb-4', isUser ? 'justify-end' : 'justify-start')}>
      <div className="flex flex-col gap-1">
        <div className="flex items-start gap-2">
          {!isUser && <div className="text-2xl mt-1">🤖</div>}
          <div className={cn('max-w-[85%] md:max-w-2xl', isUser ? 'ml-12' : '')}>
            <div
              className={cn(
                'px-4 py-3 rounded-2xl shadow-sm',
                isUser
                  ? 'bg-primary-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
              )}
            >
              {isUser ? (
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="text-sm max-w-none prose-headings:mt-2 prose-headings:mb-1 prose-p:my-1 prose-ul:my-1 prose-li:my-0 whitespace-pre-wrap">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({node, ...props}) => <a {...props} className="text-primary-600 hover:underline" target="_blank" rel="noopener noreferrer" />,
                      strong: ({node, ...props}) => <strong {...props} className="font-semibold text-gray-900" />,
                      ul: ({node, ...props}) => <ul {...props} className="list-none space-y-1 ml-0" />,
                      li: ({node, ...props}) => <li {...props} className="pl-0" />,
                      p: ({node, ...props}) => <p {...props} className="my-1" />,
                      table: ({ node, className, ...props }) => (
                        <div className="overflow-x-auto my-2">
                          <table
                            {...props}
                            className={cn(
                              'min-w-max w-full border-collapse text-sm',
                              className
                            )}
                          />
                        </div>
                      ),
                      thead: ({ node, className, ...props }) => (
                        <thead {...props} className={cn('bg-gray-50', className)} />
                      ),
                      th: ({ node, className, ...props }) => (
                        <th
                          {...props}
                          className={cn(
                            'px-3 py-2 text-left font-semibold text-gray-700 border border-gray-200 whitespace-nowrap',
                            className
                          )}
                        />
                      ),
                      td: ({ node, className, ...props }) => (
                        <td
                          {...props}
                          className={cn(
                            'px-3 py-2 text-gray-700 border border-gray-200 whitespace-nowrap',
                            className
                          )}
                        />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
          {isUser && <div className="text-2xl mt-1">👤</div>}
        </div>
        <div
          className={cn(
            'text-xs',
            isUser ? 'text-right mr-10' : 'text-left ml-10'
          )}
        >
          <span className="text-gray-500">{formatTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  );
};
