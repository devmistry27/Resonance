import { SidebarProvider, SidebarTrigger, SidebarInset } from '@/components/ui/sidebar';
import { AppSidebar } from '@/components/layout/app-sidebar';
import { ChatMessages } from '@/components/chat/chat-messages';
import { ChatInput } from '@/components/chat/chat-input';
import { useChat } from '@/hooks/use-chat';
import { SidebarSimple, CaretDown, Check } from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useState } from 'react';

export function ChatLayout() {
  const {
    conversations,
    activeConversation,
    activeConversationId,
    isLoading,
    setActiveConversationId,
    createConversation,
    deleteConversation,
    send,
    stopStreaming,
  } = useChat();

  const [selectedModel, setSelectedModel] = useState("Resonance-1o");
  const models = ["Resonance-1o"];

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex h-screen w-full overflow-hidden bg-background">
        <AppSidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          onNewConversation={createConversation}
          onDeleteConversation={deleteConversation}
        />

        <SidebarInset className="flex flex-1 flex-col overflow-hidden transition-all duration-300 ease-in-out">
          {/* Header with Model Selector */}
          <header className="flex h-14 shrink-0 items-center justify-between gap-2 px-3 transition-opacity duration-300 ease-in-out bg-background/50 backdrop-blur-sm z-10 sticky top-0">
            <div className="flex items-center gap-2">
              <SidebarTrigger>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
                  <SidebarSimple size={20} />
                </Button>
              </SidebarTrigger>
              <Separator orientation="vertical" className="h-4" />
              
              <DropdownMenu>
                <DropdownMenuTrigger>
                  <Button variant="ghost" className="h-8 gap-1 text-sm font-medium text-muted-foreground hover:text-foreground">
                    {selectedModel}
                    <CaretDown size={14} className="opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-[200px]">
                  {models.map((model) => (
                    <DropdownMenuItem 
                      key={model} 
                      onClick={() => setSelectedModel(model)}
                      className="justify-between"
                    >
                      {model}
                      {selectedModel === model && <Check size={14} />}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="flex items-center gap-2">
                 <Button variant="ghost" size="sm" className="text-muted-foreground text-xs">
                    Share
                 </Button>
            </div>
          </header>

          <div className="flex flex-1 flex-col overflow-hidden relative">
            <main className="flex-1 overflow-hidden">
              <ChatMessages
                messages={activeConversation?.messages || []}
                isLoading={isLoading}
                onSuggestionClick={(prompt) => send(prompt)}
              />
            </main>

            <ChatInput
              onSend={send}
              onStop={stopStreaming}
              isLoading={isLoading}
            />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
