# redis_memory.py
import redis.asyncio as redis
import json
from typing import List, Dict, Any
import os

class RedisChatMemory:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        
    async def connect(self):
        """Connect to Redis"""
        if not self.client:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
        
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            
    async def add_message(self, session_id: str, role: str, content: str):
        """Add a message to chat history"""
        await self.connect()
        message = {"role": role, "content": content, "timestamp": str(__import__('datetime').datetime.utcnow())}
        key = f"chat:{session_id}"
        await self.client.rpush(key, json.dumps(message))
        # Keep only last 20 messages to prevent memory issues
        await self.client.ltrim(key, -20, -1)
        
    async def get_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        await self.connect()
        key = f"chat:{session_id}"
        messages = await self.client.lrange(key, -limit, -1)
        return [json.loads(msg) for msg in messages]
        
    async def clear_messages(self, session_id: str):
        """Clear chat history for session"""
        await self.connect()
        key = f"chat:{session_id}"
        await self.client.delete(key)

# Global instance
chat_memory = RedisChatMemory()