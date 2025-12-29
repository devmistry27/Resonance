/**
 * API Service for ChatGPT Clone Backend
 */

import type {
  ChatRequest,
  ChatResponse,
  ConversationHistory,
  StreamChunk,
} from './types';

const API_BASE_URL = 'http://localhost:8000';

/**
 * Send a chat message and get a response
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * Send a chat message with streaming response
 */
export async function* streamMessage(request: ChatRequest): AsyncGenerator<StreamChunk> {
  const response = await fetch(`${API_BASE_URL}/v1/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (data) {
            try {
              const chunk: StreamChunk = JSON.parse(data);
              yield chunk;
              if (chunk.done) return;
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Get conversation history for a session
 */
export async function getConversation(sessionId: string): Promise<ConversationHistory> {
  const response = await fetch(`${API_BASE_URL}/v1/conversations/${sessionId}`);
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  return response.json();
}

/**
 * Clear conversation history for a session
 */
export async function clearConversation(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/v1/conversations/${sessionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
}

/**
 * List all active sessions
 */
export async function listSessions(): Promise<{ sessions: string[]; count: number }> {
  const response = await fetch(`${API_BASE_URL}/v1/conversations`);
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  return response.json();
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{
  status: string;
  model_loaded: boolean;
  device: string;
  model_name: string;
}> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  return response.json();
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}
