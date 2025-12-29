"""
Chat Manager
Handles conversation history, prompt construction, and search integration.
Optimized for reducing hallucination and improving factual accuracy.
"""
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from collections import OrderedDict

import config
from schemas import ChatMessage
from model_service import model_service
from search_service import search_service

logger = logging.getLogger(__name__)


class ConversationStore:
    """In-memory conversation storage with LRU eviction."""
    
    def __init__(self, max_sessions: int = 1000):
        self.sessions: OrderedDict[str, List[ChatMessage]] = OrderedDict()
        self.max_sessions = max_sessions
    
    def get(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session."""
        if session_id in self.sessions:
            self.sessions.move_to_end(session_id)
            return self.sessions[session_id]
        return []
    
    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to a session."""
        if session_id not in self.sessions:
            if len(self.sessions) >= self.max_sessions:
                self.sessions.popitem(last=False)
            self.sessions[session_id] = []
        
        self.sessions.move_to_end(session_id)
        
        if message.timestamp is None:
            message.timestamp = datetime.now()
        
        self.sessions[session_id].append(message)
    
    def clear(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_all_sessions(self) -> List[str]:
        """Get all session IDs."""
        return list(self.sessions.keys())


class ChatManager:
    """Manages chat conversations with anti-hallucination optimization."""
    
    # System prompts optimized for factual accuracy
    DEFAULT_SYSTEM = (
        "You are a helpful AI assistant. Be concise and accurate. "
        "If you don't know something, say so honestly."
    )
    
    SEARCH_SYSTEM = (
        "You are a helpful AI assistant with access to web search results. "
        "IMPORTANT: Base your answer ONLY on the search results provided below. "
        "Do NOT make up information. If the search results don't contain the answer, say so."
    )
    
    def __init__(self):
        self.store = ConversationStore()
    
    def _should_search(self, query: str) -> bool:
        """Determine if a query needs web search."""
        if not config.SEARCH_ENABLED:
            return False
            
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in config.SEARCH_TRIGGER_KEYWORDS)
    
    def _build_history_context(self, messages: List[ChatMessage]) -> str:
        """Build conversation history string."""
        if not messages:
            return ""
            
        history_parts = []
        for msg in messages:
            if msg.role == "user":
                history_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                history_parts.append(f"Assistant: {msg.content}")
        
        if history_parts:
            return "Previous conversation:\n" + "\n".join(history_parts) + "\n\n"
        return ""
    
    def _build_prompt(
        self,
        messages: List[ChatMessage],
        search_results: Optional[str] = None
    ) -> str:
        """
        Build the final prompt for the model.
        Uses Alpaca-style format optimized for instruction following.
        """
        # Get the last user message as the current instruction
        last_user_msg = ""
        history_msgs = []
        
        for msg in messages:
            if msg.role == "user":
                if last_user_msg:
                    history_msgs.append(ChatMessage(role="user", content=last_user_msg))
                last_user_msg = msg.content
            elif msg.role == "assistant":
                history_msgs.append(msg)
        
        # Build history context from previous turns
        history_context = self._build_history_context(history_msgs)
        
        # Select appropriate system prompt
        if search_results:
            system = self.SEARCH_SYSTEM
            
            # For search queries, construct extraction-focused prompt
            prompt = (
                f"{system}\n\n"
                f"### Search Results:\n{search_results}\n\n"
                f"{history_context}"
                f"### User Question:\n{last_user_msg}\n\n"
                f"### Instructions:\n"
                f"1. Answer based ONLY on the search results above\n"
                f"2. Quote specific facts, numbers, or prices directly\n"
                f"3. Cite which source you used\n"
                f"4. If the answer isn't in the results, say \"I couldn't find that information\"\n\n"
                f"### Response:\n"
            )
        else:
            system = self.DEFAULT_SYSTEM
            
            prompt = (
                f"{system}\n\n"
                f"{history_context}"
                f"### Instruction:\n{last_user_msg}\n\n"
                f"### Response:\n"
            )
        
        return prompt
    
    def _truncate_messages(
        self,
        messages: List[ChatMessage],
        max_tokens: int
    ) -> List[ChatMessage]:
        """Truncate messages to fit within token budget."""
        if not messages:
            return messages
            
        available_tokens = max_tokens - 200  # Reserve for response
        
        selected = []
        current_tokens = 0
        
        # Always include most recent messages first
        for msg in reversed(messages):
            msg_tokens = model_service.count_tokens(f"{msg.role}: {msg.content}")
            if current_tokens + msg_tokens <= available_tokens:
                selected.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return selected

    def prepare_prompt(
        self,
        session_id: str,
        new_messages: List[ChatMessage],
        max_tokens: int = None
    ) -> Tuple[str, int, Optional[List[dict]], bool]:
        """
        Prepare the full prompt for model inference.
        
        Returns: (prompt, token_count, sources, used_search)
        """
        # Get existing history
        history = self.store.get(session_id).copy()
        
        # Add new messages
        last_user_msg = None
        for msg in new_messages:
            history.append(msg)
            self.store.add_message(session_id, msg)
            if msg.role == "user":
                last_user_msg = msg
        
        # Check if we should search
        search_results = None
        sources = None
        used_search = False
        
        if last_user_msg and self._should_search(last_user_msg.content):
            logger.info(f"Search triggered for: {last_user_msg.content}")
            
            results = search_service.search(last_user_msg.content)
            
            if results:
                used_search = True
                search_results = search_service.format_results_for_prompt(results)
                sources = search_service.extract_sources_for_response(results)
                logger.info(f"Found {len(results)} search results")
        
        # Truncate history to fit context
        max_ctx = max_tokens or config.MAX_CONTEXT_TOKENS
        truncated = self._truncate_messages(history, max_ctx)
        
        # Build final prompt
        prompt = self._build_prompt(truncated, search_results)
        token_count = model_service.count_tokens(prompt)
        
        logger.debug(f"Prepared prompt with {token_count} tokens, search={used_search}")
        
        return prompt, token_count, sources, used_search
    
    def add_user_message(self, session_id: str, content: str) -> ChatMessage:
        """Add a user message to the conversation."""
        message = ChatMessage(role="user", content=content)
        self.store.add_message(session_id, message)
        return message
    
    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        sources: Optional[List[dict]] = None
    ) -> ChatMessage:
        """Add an assistant message to the conversation."""
        message = ChatMessage(role="assistant", content=content, sources=sources)
        self.store.add_message(session_id, message)
        return message
    
    def get_conversation(self, session_id: str) -> List[ChatMessage]:
        """Get full conversation history."""
        return self.store.get(session_id)
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history."""
        return self.store.clear(session_id)
    
    def get_context_token_count(self, session_id: str) -> int:
        """Get token count for current context."""
        messages = self.store.get(session_id)
        if not messages:
            return 0
        prompt = self._build_prompt(messages)
        return model_service.count_tokens(prompt)


# Global instance
chat_manager = ChatManager()
