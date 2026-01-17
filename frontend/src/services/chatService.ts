import { apiClient, handleApiError } from './api';
import { ChatRequest, ChatResponse, ApiResponse } from '@/types';

export const chatService = {
  /**
   * Send message to chat agent
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ChatResponse>>('/chat', request);
      return response.data.data!;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get chat history
   */
  async getChatHistory(): Promise<ChatResponse[]> {
    try {
      const response = await apiClient.get<ApiResponse<ChatResponse[]>>('/chat/history');
      return response.data.data || [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
