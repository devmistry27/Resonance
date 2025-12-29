/**
 * Shared Types for Chat Application
 */

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: { title: string; url: string }[];
}

export interface ChatRequest {
  session_id: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  stream?: boolean;
}

export interface UsageStats {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  usage: UsageStats;
  model: string;
}

export interface ConversationHistory {
  session_id: string;
  messages: ChatMessage[];
  total_tokens: number;
}

export interface StreamChunk {
  content: string;
  done: boolean;
  usage?: UsageStats;
  error?: string;
  sources?: { title: string; url: string }[];
}
