"""API routes for chat functionality."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from auth.jwt_handler import get_current_user_id
from agents.research_agent import run_research_agent
from tools.data_processor import process_file
from llm.minimax_client import get_minimax_client
from middleware.error_handler import sanitize_input, validate_input_length
from supabase import create_client
from config import settings
import json


router = APIRouter(prefix="/api/chat", tags=["chat"])

# Supabase client
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)


class ChatRequest(BaseModel):
    """Chat request model."""
    conversation_id: Optional[str] = None
    message: str
    enable_search: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""
    message_id: str
    response: str
    sources: List[dict] = []
    thinking_trace: List[dict] = []


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Send a chat message and get response."""
    # Sanitize and validate input
    message = sanitize_input(request.message)
    validate_input_length(message)

    # Get or create conversation
    if request.conversation_id:
        conv_id = request.conversation_id
    else:
        # Create new conversation
        result = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": message[:50]  # First 50 chars as title
        }).execute()
        conv_id = result.data[0]["id"]

    # Save user message
    user_msg = supabase.table("messages").insert({
        "conversation_id": conv_id,
        "role": "user",
        "content": message
    }).execute()

    # Get conversation history
    history_result = supabase.table("messages")\
        .select("role, content")\
        .eq("conversation_id", conv_id)\
        .order("timestamp", desc=False)\
        .execute()

    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history_result.data[:-1]  # Exclude current message
    ]

    # Run agent if search is enabled
    if request.enable_search:
        try:
            agent_result = await run_research_agent(message, messages)
            response_text = agent_result["response"]
            sources = agent_result.get("sources", [])
            thinking_trace = agent_result.get("thinking_trace", [])
        except Exception as e:
            # Fallback to LLM
            request.enable_search = False
    else:
        # Use LLM directly without search
        try:
            client = get_minimax_client()
            messages.append({"role": "user", "content": message})
            llm_response = await client.generate_response(messages)
            response_text = llm_response["content"]
            sources = []
            thinking_trace = llm_response.get("thinking_trace", [])
        except ValueError:
            response_text = "I'm currently unavailable. Please configure the required API keys (MINIMAX_API_KEY, TAVILY_API_KEY) to enable full functionality."
            sources = []
            thinking_trace = []
    
    # Save assistant message
    assistant_msg = supabase.table("messages").insert({
        "conversation_id": conv_id,
        "role": "assistant",
        "content": response_text,
        "thinking_trace": thinking_trace,
        "sources": sources
    }).execute()
    
    # Save sources
    if sources:
        for source in sources:
            supabase.table("sources").insert({
                "message_id": assistant_msg.data[0]["id"],
                "url": source.get("url"),
                "title": source.get("title"),
                "content": source.get("content", "")[:500],
                "credibility_score": source.get("score", 0.0)
            }).execute()
    
    return ChatResponse(
        message_id=assistant_msg.data[0]["id"],
        response=response_text,
        sources=sources,
        thinking_trace=thinking_trace
    )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Stream a chat response."""
    message = sanitize_input(request.message)
    validate_input_length(message)
    
    # Get or create conversation
    if request.conversation_id:
        conv_id = request.conversation_id
    else:
        result = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": message[:50]
        }).execute()
        conv_id = result.data[0]["id"]
    
    # Save user message
    supabase.table("messages").insert({
        "conversation_id": conv_id,
        "role": "user",
        "content": message
    }).execute()
    
    # Get conversation history
    history_result = supabase.table("messages")\
        .select("role, content")\
        .eq("conversation_id", conv_id)\
        .order("timestamp", desc=False)\
        .execute()
    
    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history_result.data[:-1]
    ]
    messages.append({"role": "user", "content": message})
    
    async def generate():
        """Generate streaming response."""
        try:
            client = get_minimax_client()
            full_response = ""
            thinking_traces = []
            
            async for chunk in client.generate_streaming_response(messages):
                if chunk["type"] == "text_delta":
                    full_response += chunk["text"]
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk['text']})}\n\n"
                elif chunk["type"] == "thinking_delta":
                    thinking_traces.append(chunk["thinking"])
                    yield f"data: {json.dumps({'type': 'thinking', 'content': chunk['thinking']})}\n\n"
                elif chunk["type"] == "done":
                    # Save assistant message
                    supabase.table("messages").insert({
                        "conversation_id": conv_id,
                        "role": "assistant",
                        "content": full_response,
                        "thinking_trace": thinking_traces
                    }).execute()
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            error_msg = "Streaming unavailable. Please configure MINIMAX_API_KEY."
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """Upload and process a file (CSV or PDF)."""
    # Validate file size (50MB limit)
    content = await file.read()
    if len(content) > 52428800:  # 50MB
        raise HTTPException(status_code=400, detail="File too large. Maximum 50MB.")
    
    # Process file
    result = await process_file(content, file.filename, file.content_type)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Save to database
    file_record = supabase.table("file_uploads").insert({
        "user_id": user_id,
        "filename": file.filename,
        "file_type": file.content_type,
        "file_size": len(content),
        "processed_at": "now()",
        "insights": result
    }).execute()
    
    return {
        "file_id": file_record.data[0]["id"],
        "filename": file.filename,
        "insights": result
    }


@router.get("/conversations")
async def get_conversations(user_id: str = Depends(get_current_user_id)):
    """Get user's conversation list."""
    result = supabase.table("conversations")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("updated_at", desc=True)\
        .execute()
    
    return {"conversations": result.data}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get conversation messages."""
    # Verify ownership
    conv = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .eq("user_id", user_id)\
        .maybeSingle()\
        .execute()
    
    if not conv.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("timestamp", desc=False)\
        .execute()
    
    return {
        "conversation": conv.data,
        "messages": messages.data
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a conversation."""
    # Verify ownership
    conv = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .eq("user_id", user_id)\
        .maybeSingle()\
        .execute()
    
    if not conv.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete messages first
    supabase.table("messages")\
        .delete()\
        .eq("conversation_id", conversation_id)\
        .execute()
    
    # Delete conversation
    supabase.table("conversations")\
        .delete()\
        .eq("id", conversation_id)\
        .execute()
    
    return {"message": "Conversation deleted successfully"}
