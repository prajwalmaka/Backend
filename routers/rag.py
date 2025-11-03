
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import InterviewBooking
from services.rag_service import RAGService
#from services.rag_service import generate_response
from redis_memory import RedisChatMemory
import uuid

router = APIRouter(prefix="/rag", tags=["RAG"])

# Dependency for Redis memory
async def get_chat_memory():
    memory = RedisChatMemory()
    await memory.connect()
    return memory

async def get_rag_service():
    return RAGService()


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    contexts_used: int

class InterviewBookingRequest(BaseModel):
    name: str
    email: EmailStr
    date: str  # YYYY-MM-DD
    time: str  # HH:MM

class InterviewBookingResponse(BaseModel):
    booking_id: str
    name: str
    email: str
    date: str
    time: str
    status: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_rag(
    request: ChatRequest,
    chat_memory: RedisChatMemory = Depends(get_chat_memory),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Chat endpoint with RAG and memory"""
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = await rag_service.generate_response(request.message, session_id, chat_memory)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/book-interview", response_model=InterviewBookingResponse)
async def book_interview(
    booking: InterviewBookingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Book an interview slot"""
    
    try:
        # Create booking record
        interview = InterviewBooking(
            name=booking.name,
            email=booking.email,
            date=booking.date,
            time=booking.time
        )
        
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        
        return InterviewBookingResponse(
            booking_id=interview.id,
            name=interview.name,
            email=interview.email,
            date=interview.date,
            time=interview.time,
            status=interview.status
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

@router.get("/chat-history/{session_id}")
async def get_chat_history(
    session_id: str,
    chat_memory: RedisChatMemory = Depends(get_chat_memory)
):
    """Get chat history for session"""
    try:
        messages = await chat_memory.get_messages(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.delete("/chat-history/{session_id}")
async def clear_chat_history(
    session_id: str,
    chat_memory: RedisChatMemory = Depends(get_chat_memory)
):
    """Clear chat history for session"""
    try:
        await chat_memory.clear_messages(session_id)
        return {"message": "Chat history cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")