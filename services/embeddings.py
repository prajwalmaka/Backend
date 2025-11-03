from typing import List
from sentence_transformers import SentenceTransformer
import asyncio

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

async def generate_embeddings(texts: List[str], model: str = "transformer") -> List[List[float]]:
    transformer_model = _get_model()

    def _encode_sync():
        return transformer_model.encode(texts).tolist()

    embeddings = await asyncio.to_thread(_encode_sync)
    return embeddings

def generate_embeddings_sync(texts: List[str]) -> List[List[float]]:
    transformer_model = _get_model()
    return transformer_model.encode(texts).tolist()
