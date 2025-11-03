

import os
from typing import List, Dict, Any
from services.vectorstore_base import VectorStore
from pinecone import Pinecone, ServerlessSpec
import asyncio

INDEX_NAME = "backend"

def init_pinecone():
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY is not set")

    pc = Pinecone(api_key=api_key)

    # Only create if not exists
    if INDEX_NAME not in pc.list_indexes():
        try:
            pc.create_index(
                name=INDEX_NAME,
                dimension=384,  # CHANGED FROM 1536 to 384 for transformer model
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        except Exception as e:
            if "ALREADY_EXISTS" not in str(e):
                raise 

    return pc.Index(INDEX_NAME)

class PineconeVectorStore(VectorStore):
    _index = None  # class-level shared index

    def __init__(self):
        if PineconeVectorStore._index is None:
            PineconeVectorStore._index = init_pinecone()
        self.index = PineconeVectorStore._index

    async def add_vectors(
        self, vectors: List[List[float]], metadata: List[Dict[str, Any]], ids: List[str]
    ) -> None:
        """Add vectors to Pinecone index"""
        items = [{"id": ids[i], "values": vectors[i], "metadata": metadata[i]} for i in range(len(ids))]
        await asyncio.to_thread(self.index.upsert, vectors=items)

    async def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Query Pinecone index for top_k similar vectors"""
        res = await asyncio.to_thread(
            self.index.query,
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        return [match["metadata"] for match in res["matches"]]
