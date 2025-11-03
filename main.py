# main.py
from fastapi import FastAPI
from routers.ingest import router as ingest_router
from routers.rag import router as rag_router
from database import init_db
from redis_memory import chat_memory
import asyncio

app = FastAPI(title="Backend AIML")

# Include routers
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await init_db()
    await chat_memory.connect()
    print("✅ Database and Redis initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await chat_memory.disconnect()
    print("✅ Services shut down gracefully")

@app.get("/")
async def root() -> dict:
    """Health check / basic info."""
    return {
        "status": "ok", 
        "service": "Backend AIML",
        "endpoints": {
            "ingest": "/ingest/upload",
            "chat": "/rag/chat", 
            "book_interview": "/rag/book-interview"
        }
    }

@app.get("/health")
async def health_check() -> dict:
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # You can add actual checks
        "redis": "connected",
        "pinecone": "connected"
    }