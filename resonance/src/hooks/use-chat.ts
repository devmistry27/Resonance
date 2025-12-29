import { useState, useCallback, useRef, useEffect } from 'react';
import {
  type ChatMessage,
} from '@/lib/types';
import {
  sendMessage,
  streamMessage,
  clearConversation,
  generateSessionId,
} from '@/lib/api';

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState<string>('');
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Get active conversation
  const activeConversation = conversations.find((c) => c.id === activeConversationId);

  // Create a new conversation
  const createConversation = useCallback(() => {
    const newConversation: Conversation = {
      id: generateSessionId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    return newConversation;
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback(async (id: string) => {
    try {
      await clearConversation(id);
    } catch {
      // Ignore errors - conversation might not exist on server
    }
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      const remaining = conversations.filter((c) => c.id !== id);
      setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  }, [activeConversationId, conversations]);

  // Update conversation title based on first message
  const updateConversationTitle = useCallback((id: string, firstMessage: string) => {
    const title = firstMessage.slice(0, 30) + (firstMessage.length > 30 ? '...' : '');
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title } : c))
    );
  }, []);

  // Add a message to the active conversation
  const addMessage = useCallback((message: ChatMessage) => {
    if (!activeConversationId) return;
    
    setConversations((prev) =>
      prev.map((c) =>
        c.id === activeConversationId
          ? {
              ...c,
              messages: [...c.messages, message],
              updatedAt: new Date(),
            }
          : c
      )
    );
  }, [activeConversationId]);

  // Update the last assistant message (for streaming)
  const updateLastAssistantMessage = useCallback((content: string, sources?: { title: string; url: string }[]) => {
    if (!activeConversationId) return;
    
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== activeConversationId) return c;
        
        const messages = [...c.messages];
        const lastIndex = messages.length - 1;
        
        if (lastIndex >= 0 && messages[lastIndex].role === 'assistant') {
          // Only update sources if provided, otherwise keep existing
          const updatedSources = sources || messages[lastIndex].sources;
          messages[lastIndex] = { ...messages[lastIndex], content, sources: updatedSources };
        }
        
        return { ...c, messages, updatedAt: new Date() };
      })
    );
  }, [activeConversationId]);

  // Send a message (with streaming)
  const send = useCallback(async (content: string, useStreaming = true) => {
    if (!content.trim()) return;
    
    setError(null);
    
    // Create conversation if none exists
    let conversationId = activeConversationId;
    if (!conversationId) {
      const newConv = createConversation();
      conversationId = newConv.id;
    }

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content };
    addMessage(userMessage);

    // Update title if first message
    const conversation = conversations.find((c) => c.id === conversationId);
    if (conversation && conversation.messages.length === 0) {
      updateConversationTitle(conversationId, content);
    }

    setIsLoading(true);
    setStreamingContent('');

    try {
      // Get all messages for context
      const allMessages = conversation
        ? [...conversation.messages, userMessage]
        : [userMessage];

      if (useStreaming) {
        // Add placeholder assistant message
        const assistantMessage: ChatMessage = { role: 'assistant', content: '' };
        addMessage(assistantMessage);

        let fullContent = '';
        
        for await (const chunk of streamMessage({
          session_id: conversationId,
          messages: [userMessage], // Only send new message, server has history
        })) {
          if (chunk.error) {
            throw new Error(chunk.error);
          }
          
          
          fullContent += chunk.content;
          setStreamingContent(fullContent);
          
          // Pass sources if available (on final chunk usually)
          updateLastAssistantMessage(fullContent, chunk.sources);
          
          if (chunk.done) break;
        }
      } else {
        const response = await sendMessage({
          session_id: conversationId,
          messages: [userMessage],
        });

        addMessage(response.message);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message
      addMessage({
        role: 'assistant',
        content: `Error: ${errorMessage}`,
      });
    } finally {
      setIsLoading(false);
      setStreamingContent('');
    }
  }, [
    activeConversationId,
    addMessage,
    conversations,
    createConversation,
    updateConversationTitle,
    updateLastAssistantMessage,
  ]);

  // Stop streaming
  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  // Initialize with a conversation if none exists
  useEffect(() => {
    if (conversations.length === 0) {
      createConversation();
    }
  }, []);

  return {
    conversations,
    activeConversation,
    activeConversationId,
    isLoading,
    error,
    streamingContent,
    setActiveConversationId,
    createConversation,
    deleteConversation,
    send,
    stopStreaming,
  };
}
