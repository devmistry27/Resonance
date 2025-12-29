import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuAction,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';

import { Plus, ChatCircle, Trash, Gear, Command } from '@phosphor-icons/react';
import { type Conversation } from '@/hooks/use-chat';


interface AppSidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

export function AppSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}: AppSidebarProps) {
  // Group conversations by date
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const isToday = (date: Date) => date.toDateString() === today.toDateString();
  const isYesterday = (date: Date) => date.toDateString() === yesterday.toDateString();

  const groupedConversations = {
    today: conversations.filter((c) => isToday(c.updatedAt)),
    yesterday: conversations.filter((c) => isYesterday(c.updatedAt)),
    older: conversations.filter((c) => !isToday(c.updatedAt) && !isYesterday(c.updatedAt)),
  };

  return (
      <Sidebar className="border-r">
        <SidebarHeader className="p-2">
           <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Resonance</span>
                  <span className="truncate text-xs">Standard</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
         
          <div className="pt-2">
            <Button
              onClick={onNewConversation}
              variant="outline"
              className="w-full justify-start gap-2"
            >
              <Plus weight="bold" size={16} />
              New Chat
            </Button>
          </div>
        </SidebarHeader>

        <SidebarContent>
            {/* Today */}
            {groupedConversations.today.length > 0 && (
              <SidebarGroup>
                <SidebarGroupLabel>Today</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {groupedConversations.today.map((conversation) => (
                      <ConversationItem
                        key={conversation.id}
                        conversation={conversation}
                        isActive={activeConversationId === conversation.id}
                        onSelect={() => onSelectConversation(conversation.id)}
                        onDelete={() => onDeleteConversation(conversation.id)}
                      />
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            )}

            {/* Yesterday */}
            {groupedConversations.yesterday.length > 0 && (
              <SidebarGroup>
                <SidebarGroupLabel>Yesterday</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {groupedConversations.yesterday.map((conversation) => (
                      <ConversationItem
                        key={conversation.id}
                        conversation={conversation}
                        isActive={activeConversationId === conversation.id}
                        onSelect={() => onSelectConversation(conversation.id)}
                        onDelete={() => onDeleteConversation(conversation.id)}
                      />
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            )}

            {/* Older */}
            {groupedConversations.older.length > 0 && (
              <SidebarGroup>
                <SidebarGroupLabel>Previous</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {groupedConversations.older.map((conversation) => (
                      <ConversationItem
                        key={conversation.id}
                        conversation={conversation}
                        isActive={activeConversationId === conversation.id}
                        onSelect={() => onSelectConversation(conversation.id)}
                        onDelete={() => onDeleteConversation(conversation.id)}
                      />
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            )}
        </SidebarContent>

        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="sm">
                <Gear size={16} />
                <span>Settings</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>

  );
}

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function ConversationItem({ conversation, isActive, onSelect, onDelete }: ConversationItemProps) {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        onClick={onSelect}
        isActive={isActive}
        className="group/item"
      >
        <ChatCircle weight={isActive ? 'fill' : 'regular'} />
        <span>{conversation.title}</span>
      </SidebarMenuButton>
        <SidebarMenuAction
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          showOnHover
        >
          <Trash />
        </SidebarMenuAction>
    </SidebarMenuItem>
  );
}
