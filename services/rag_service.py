from typing import List, Dict, Any
from services.embeddings import generate_embeddings
from services.vectorstore_pinecone import PineconeVectorStore
from redis_memory import RedisChatMemory  # Import the class instead

class RAGService:
    def __init__(self):
        self.vectorstore = PineconeVectorStore()
        
    async def get_context(self, query: str, top_k: int = 3) -> List[str]:
        """Get relevant context for query"""
        query_embedding = await generate_embeddings([query])
        results = await self.vectorstore.query(query_embedding[0], top_k=top_k)
        
        # Extract content from metadata
        contexts = []
        for result in results:
            content = result.get('content', '')
            if content:
                contexts.append(content)
                
        return contexts
    
    async def format_prompt(self, query: str, contexts: List[str], chat_history: List[Dict]) -> str:
        """Format the prompt with context and chat history"""
        
        # Build context string
        context_str = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts)])
        
        # Build chat history
        history_str = ""
        for msg in chat_history[-6:]:  # Last 6 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        
        prompt = f"""Based on the following context and conversation history, answer the user's question.

Available Context:
{context_str}

Conversation History:
{history_str}

User Question: {query}

Please provide a helpful answer based on the context. If the context doesn't contain relevant information, say so politely."""
        
        return prompt
    
    async def generate_response(self, query: str, session_id: str, chat_memory: RedisChatMemory) -> Dict[str, Any]:
        """Generate RAG response with chat memory"""
        
        # Get chat history
        chat_history = await chat_memory.get_messages(session_id)
        
        # Get relevant context
        contexts = await self.get_context(query)
        
        # Format prompt (in real scenario, you'd use an LLM here)
        prompt = await self.format_prompt(query, contexts, chat_history)
        
        # For demo purposes, we'll create a simple response
        # In production, you'd call an LLM API here
        if contexts:
            response_text = f"I found some relevant information: {contexts[0][:200]}..."
        else:
            response_text = "I couldn't find specific information about that in the uploaded documents. Could you please provide more details?"
        
        # Store messages in memory
        await chat_memory.add_message(session_id, "user", query)
        await chat_memory.add_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "contexts_used": len(contexts),
            "session_id": session_id
        }

# Global instance
rag_service = RAGService()