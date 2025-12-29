"""
Pydantic Schemas for API Request/Response Models
Clean, validated schemas for the chat API.
"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SearchResult(BaseModel):
    """Individual search result from web search."""
    title: str
    url: str
    snippet: str
    
    
class ChatMessage(BaseModel):
    """Individual chat message."""
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None
    sources: Optional[List[SearchResult]] = None
    
    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class ChatRequest(BaseModel):
    """Request body for chat completion."""
    session_id: str = Field(
        default="default", 
        description="Session ID for conversation tracking",
        min_length=1,
        max_length=100
    )
    messages: List[ChatMessage] = Field(
        ..., 
        description="List of messages in the conversation",
        min_length=1
    )
    temperature: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature (0=deterministic, higher=more random)"
    )
    max_tokens: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=1024, 
        description="Maximum tokens to generate"
    )
    top_p: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Top-p (nucleus) sampling"
    )
    stream: bool = Field(
        default=False, 
        description="Whether to stream the response"
    )


class UsageStats(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class ChatResponse(BaseModel):
    """Response from chat completion."""
    session_id: str
    message: ChatMessage
    usage: UsageStats
    model: str = "resonance-gpt"
    search_performed: bool = False


class StreamChunk(BaseModel):
    """Single chunk in streaming response."""
    content: str
    done: bool = False
    usage: Optional[UsageStats] = None
    sources: Optional[List[SearchResult]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy", "degraded"]
    model_loaded: bool
    search_available: bool
    device: str
    model_name: str
    version: str = "2.0.0"


class ConversationHistory(BaseModel):
    """Conversation history response."""
    session_id: str
    messages: List[ChatMessage]
    total_tokens: int
    message_count: int


class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
