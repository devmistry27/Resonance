import { type ChatMessage } from '@/lib/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, Sparkle } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface ChatMessageItemProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export function ChatMessageItem({ message, isStreaming }: ChatMessageItemProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "group w-full py-8 transition-colors bg-transparent"    
      )}
    >
      <div className="mx-auto flex max-w-3xl gap-6 px-4">
        <div className="flex-shrink-0 pt-1">
          <Avatar className={cn(
            "h-8 w-8 border shadow-sm transition-transform group-hover:scale-105",
            isUser ? "bg-card" : "bg-primary text-primary-foreground border-transparent"
          )}>
            <AvatarFallback className={isUser ? "bg-transparent text-muted-foreground" : "bg-primary text-primary-foreground"}>
              {isUser ? <User size={16} weight="bold" /> : <Sparkle size={16} weight="fill" />}
            </AvatarFallback>
          </Avatar>
        </div>

        <div className="flex-1 space-y-2 overflow-hidden">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground/90">
              {isUser ? "You" : "Resonance"}
            </span>
          </div>
          
          <div className={cn("prose prose-neutral dark:prose-invert max-w-none text-[15px] leading-relaxed break-words", isUser ? "text-white" : "text-foreground")}>
            {message.content || (
              <span className="animate-pulse">Thinking...</span>
            )}
            {isStreaming && (
              <span className="ml-1 inline-block h-4 w-1.5 animate-pulse bg-primary align-middle text-white" />
            )}
          </div>

          {/* Sources Chips */}
          {message.sources && message.sources.length > 0 && (
            <div className="pt-2 flex flex-wrap gap-2">
              {message.sources.map((source, i) => (
                <a 
                  key={i}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-secondary/50 hover:bg-secondary text-xs font-medium transition-colors no-underline border border-transparent hover:border-border/50"
                >
                  <div className="w-4 h-4 rounded-full bg-background flex items-center justify-center shrink-0 text-[10px] text-muted-foreground uppercase border">
                    {i + 1}
                  </div>
                  <span className="truncate max-w-[150px]">{source.title}</span>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
