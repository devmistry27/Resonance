import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { PaperPlaneRight, Stop, Paperclip, Globe } from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, onStop, isLoading, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isLoading && !disabled) {
      onSend(input.trim());
      setInput('');
      // Reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-gradient-to-t from-background via-background to-transparent pb-6 pt-10 px-4">
      <div className="mx-auto max-w-3xl">
        <motion.div 
          initial={false}
          animate={{
            boxShadow: isFocused ? "0 4px 20px -2px rgba(0, 0, 0, 0.1)" : "0 2px 10px -1px rgba(0, 0, 0, 0.05)"
          }}
          transition={{ duration: 0.2 }}
          className={cn(
            "relative flex flex-col gap-2 rounded-xl border bg-card/80 p-3 shadow-lg backdrop-blur-xl transition-all",
            "dark:bg-card/40 dark:border-white/10"
          )}
        >
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask Resonance anything..."
            disabled={disabled}
            className="min-h-[44px] max-h-[200px] w-full resize-none border-0 bg-transparent px-3 py-2 text-base  placeholder:text-muted-foreground focus-visible:ring-0 focus-visible:ring-offset-0 disabled:opacity-50"
            rows={1}
          />
          
          <div className="flex items-center justify-between px-2 pb-1">
            <div className="flex items-center gap-2">
              <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 text-muted-foreground hover:bg-muted/50 hover:text-foreground rounded-lg transition-colors"
                title="Attach file (Coming soon)"
              >
                <Paperclip size={18} />
              </Button>
              <Button
                size="icon"
                variant="ghost" 
                className="h-8 w-8 text-muted-foreground hover:bg-muted/50 hover:text-foreground rounded-lg transition-colors"
                title="Search Web"
                onClick={() => setInput(prev => "Search for " + prev)}
              >
                <Globe size={18} />
              </Button>
            </div>

            <Button
              size="icon"
              onClick={isLoading ? onStop : handleSubmit}
              disabled={!input.trim() && !isLoading}
              className={cn(
                "h-8 w-8 rounded-lg transition-all duration-200",
                input.trim() || isLoading 
                  ? "bg-primary text-primary-foreground opacity-100 shadow-md" 
                  : "bg-muted text-muted-foreground opacity-50 shadow-none cursor-not-allowed"
              )}
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div
                    key="stop"
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.5, opacity: 0 }}
                  >
                    <Stop weight="fill" size={14} />
                  </motion.div>
                ) : (
                  <motion.div
                    key="send"
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.5, opacity: 0 }}
                  >
                    <PaperPlaneRight weight="fill" size={14} />
                  </motion.div>
                )}
              </AnimatePresence>
            </Button>
          </div>
        </motion.div>
        
        <div className="mt-3 flex justify-center">
        <p className="text-center text-[10px] text-muted-foreground/60 select-none">
          Resonance can make mistakes. Check important info.
        </p>
        </div>
      </div>
    </div>
  );
}
