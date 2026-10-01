"""
Vector Embeddings Generator for CartIQ ChromaDB Integration.
"""

import math
from typing import List

class SimpleEmbeddingGenerator:
    """
    Lightweight, deterministic vector embedding generator.
    Produces 128-dimensional normalized embedding vectors for fast, offline similarity matching in ChromaDB.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dim
        vec = [0.0] * self.dim
        words = text.lower().split()
        for idx, word in enumerate(words):
            hash_val = hash(word)
            pos = abs(hash_val) % self.dim
            vec[pos] += 1.0 + (idx * 0.05)
        
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_text(text)
