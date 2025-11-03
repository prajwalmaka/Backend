from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Simple RAG API",
    description="A working version of document upload and chat",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
documents = []
chats = {}

@app.get("/")
async def root():
    return {"message": "✅ Server is working!", "status": "active"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chunk_strategy: str = Form("paragraph")
):
    """
    Simple file upload that definitely works
    """
    try:
        print(f"📁 Received file: {file.filename}")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8') if isinstance(content, bytes) else str(content)
        
        # Store document info
        doc_info = {
            "filename": file.filename,
            "size": len(text_content),
            "content_preview": text_content[:100] + "..." if len(text_content) > 100 else text_content,
            "chunk_strategy": chunk_strategy
        }
        documents.append(doc_info)
        
        return {
            "success": True,
            "filename": file.filename,
            "message": "File uploaded successfully",
            "text_length": len(text_content),
            "preview": text_content[:100]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }

@app.post("/chat")
async def chat(message: str, session_id: str = "default"):
    """
    Simple chat that definitely works
    """
    try:
        # Initialize session if new
        if session_id not in chats:
            chats[session_id] = []
        
        # Add user message
        chats[session_id].append({"role": "user", "content": message})
        
        # Simple response logic
        if "hello" in message.lower() or "hi" in message.lower():
            response = "Hello! I'm your assistant. How can I help you today?"
        elif "upload" in message.lower():
            doc_count = len(documents)
            response = f"I see you have {doc_count} documents uploaded. I can help you search through them!"
        elif "interview" in message.lower():
            response = "I can help schedule interviews! Please provide: name, email, date, and time."
        else:
            response = f"I understand: '{message}'. How can I assist you?"
        
        # Add assistant response
        chats[session_id].append({"role": "assistant", "content": response})
        
        return {
            "success": True,
            "response": response,
            "session_id": session_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Chat failed: {str(e)}"
        }

@app.get("/documents")
async def list_documents():
    return {
        "count": len(documents),
        "documents": documents
    }

@app.get("/chat/history/{session_id}")
async def get_history(session_id: str):
    history = chats.get(session_id, [])
    return {
        "session_id": session_id,
        "history": history
    }

if __name__ == "__main__":
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("⏹️  Press CTRL+C to stop the server")
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True)