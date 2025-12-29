"""
Resonance API Server
FastAPI backend for GPT-2 based chat with web search integration.
"""
import asyncio
import logging
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

import config
from schemas import (
    ChatRequest, ChatResponse, ChatMessage, UsageStats,
    HealthResponse, ConversationHistory, StreamChunk, SearchResult
)
from model_service import model_service
from chat_manager import chat_manager
from search_service import search_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - load model on startup."""
    logger.info("=" * 50)
    logger.info("Starting Resonance API Server")
    logger.info("=" * 50)
    
    success = model_service.load_model()
    if not success:
        logger.warning("Model failed to load. API will return errors.")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="Resonance API",
    description="AI Chat API with GPT-2 and Web Search",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# =============================================================================
# Health & Info Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health and service status."""
    return HealthResponse(
        status="healthy" if model_service.is_loaded else "unhealthy",
        model_loaded=model_service.is_loaded,
        search_available=search_service.is_available,
        device=str(model_service.device) if model_service.device else "not set",
        model_name="resonance-gpt",
    )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Resonance API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


# =============================================================================
# Chat Endpoints
# =============================================================================

@app.post("/v1/chat/completions", response_model=ChatResponse, tags=["Chat"])
async def chat_completions(request: ChatRequest):
    """
    Generate a chat completion.
    Automatically uses web search for queries requiring real-time information.
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    
    try:
        # Prepare prompt with optional search
        prompt, prompt_tokens, sources, used_search = chat_manager.prepare_prompt(
            session_id=request.session_id,
            new_messages=request.messages,
            max_tokens=request.max_tokens,
        )
        
        # Use lower temperature for factual/search queries
        temperature = request.temperature
        if temperature is None:
            temperature = config.FACTUAL_TEMPERATURE if used_search else config.DEFAULT_TEMPERATURE
        
        # Generate response
        generated_text, _, completion_tokens = model_service.generate(
            prompt=prompt,
            max_tokens=request.max_tokens or config.DEFAULT_MAX_TOKENS,
            temperature=temperature,
            top_p=request.top_p or config.DEFAULT_TOP_P,
        )
        
        # Convert sources to SearchResult objects if present
        source_objects = None
        if sources:
            source_objects = [
                SearchResult(
                    title=s.get("title", ""),
                    url=s.get("url", ""),
                    snippet=s.get("snippet", "")
                ) for s in sources
            ]
        
        # Store assistant response
        assistant_msg = chat_manager.add_assistant_message(
            request.session_id,
            generated_text,
            sources=source_objects
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=assistant_msg,
            usage=UsageStats(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            search_performed=used_search,
        )
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Generate a streaming chat completion using Server-Sent Events.
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            prompt, prompt_tokens, sources, used_search = chat_manager.prepare_prompt(
                session_id=request.session_id,
                new_messages=request.messages,
                max_tokens=request.max_tokens,
            )
            
            temperature = request.temperature
            if temperature is None:
                temperature = config.FACTUAL_TEMPERATURE if used_search else config.DEFAULT_TEMPERATURE
            
            full_response = ""
            
            # Convert sources for response
            source_objects = None
            if sources:
                source_objects = [
                    {"title": s.get("title", ""), "url": s.get("url", ""), "snippet": s.get("snippet", "")}
                    for s in sources
                ]
            
            for token_text, is_done, _, completion_tokens in model_service.generate_stream(
                prompt=prompt,
                max_tokens=request.max_tokens or config.DEFAULT_MAX_TOKENS,
                temperature=temperature,
                top_p=request.top_p or config.DEFAULT_TOP_P,
            ):
                full_response += token_text
                
                chunk = StreamChunk(
                    content=token_text,
                    done=is_done,
                    usage=UsageStats(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    ) if is_done else None,
                    sources=source_objects if is_done else None,
                )
                
                yield json.dumps(chunk.model_dump())
                
                if is_done:
                    chat_manager.add_assistant_message(
                        request.session_id,
                        full_response.strip(),
                        sources=source_objects
                    )
                    break
                
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield json.dumps({"error": str(e), "done": True})
    
    return EventSourceResponse(generate_stream())


# =============================================================================
# Conversation Management
# =============================================================================

@app.get("/v1/conversations/{session_id}", response_model=ConversationHistory, tags=["Conversations"])
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    messages = chat_manager.get_conversation(session_id)
    token_count = chat_manager.get_context_token_count(session_id)
    
    return ConversationHistory(
        session_id=session_id,
        messages=messages,
        total_tokens=token_count,
        message_count=len(messages),
    )


@app.delete("/v1/conversations/{session_id}", tags=["Conversations"])
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    success = chat_manager.clear_conversation(session_id)
    return {
        "success": success,
        "message": f"Conversation {session_id} cleared" if success else f"No conversation found"
    }


@app.get("/v1/conversations", tags=["Conversations"])
async def list_conversations():
    """List all active session IDs."""
    sessions = chat_manager.store.get_all_sessions()
    return {"sessions": sessions, "count": len(sessions)}


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
