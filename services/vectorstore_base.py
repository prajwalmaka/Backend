from typing import List, Dict, Any
from abc import ABC, abstractmethod

class VectorStore(ABC):
    @abstractmethod
    async def add_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], ids: List[str]) -> None:
        pass

    @abstractmethod
    async def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass
