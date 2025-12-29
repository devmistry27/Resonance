import { useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessageItem } from './chat-message';
import { type ChatMessage } from '@/lib/types';
import { Sparkle, Code, Image, Lightbulb, PenNib } from '@phosphor-icons/react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onSuggestionClick?: (suggestion: string) => void;
}

export function ChatMessages({ messages, isLoading, onSuggestionClick }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const suggestions = [
    { label: 'Explain quantum physics', icon: Lightbulb, prompt: 'Explain quantum physics in simple terms' },
    { label: 'Write a poem', icon: PenNib, prompt: 'Write a haiku about artificial intelligence' },
    { label: 'Debug React code', icon: Code, prompt: 'Help me debug a React useEffect hook that is looping infinitey' },
    { label: 'Generate image prompt', icon: Image, prompt: 'Generate a prompt for a cyberpunk city landscape' },
  ];

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center animate-in fade-in duration-500">
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex h-16 w-16 items-center justify-center rounded-2xl bg-secondary/50 shadow-sm mb-6 ring-1 ring-border/50 backdrop-blur-sm"
        >
          <Sparkle weight="fill" className="h-8 w-8 text-primary" />
        </motion.div>
        <motion.h2 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-2xl font-semibold tracking-tight text-foreground mb-8"
        >
          How can I help you today?
        </motion.h2>

        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full"
        >
          {suggestions.map((suggestion, index) => (
            <Button
              key={index}
              variant="outline"
              className="h-auto py-4 px-4 justify-start gap-4 text-left whitespace-normal hover:bg-secondary/50 hover:border-primary/20 transition-all duration-300"
              onClick={() => onSuggestionClick?.(suggestion.prompt)}
            >
              <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary/10 text-primary shrink-0">
                <suggestion.icon size={18} weight="duotone" />
              </div>
              <span className="text-sm font-medium text-foreground/80">{suggestion.label}</span>
            </Button>
          ))}
        </motion.div>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full px-0" ref={scrollRef}>
      <div className="flex flex-col pb-4">
        {messages.map((message, index) => (
          <ChatMessageItem
            key={index}
            message={message}
            isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
          />
        ))}
        <div ref={bottomRef} className="h-4" />
      </div>
    </ScrollArea>
  );
}
