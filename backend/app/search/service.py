from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.embedding.service import EmbeddingService


class SemanticSearchService:
    """Semantic retrieval service using FAISS with cosine similarity."""

    def __init__(self, index_path: str | None = None, embedding_service: EmbeddingService | None = None) -> None:
        self._index_path = index_path or os.getenv("FAISS_INDEX_PATH", "./data/faiss_index.index")
        self._embedding_service = embedding_service or EmbeddingService()
        self._documents: list[str] = []
        self._index: faiss.Index | None = None
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        path = Path(self._index_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self._index = faiss.read_index(str(path))
            if path.with_suffix(".json").exists():
                self._documents = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
            return
        self._index = faiss.IndexFlatIP(384)

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms

    def add_documents(self, documents: list[str]) -> None:
        if not documents:
            return
        embeddings = self._embedding_service.embed_batch(documents)
        vectors = np.array(embeddings, dtype="float32")
        vectors = self._normalize_vectors(vectors)
        if self._index is None:
            self._index = faiss.IndexFlatIP(vectors.shape[1])
        self._index.add(vectors)
        self._documents.extend(documents)
        self._persist()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        query_vector = np.array([self._embedding_service.embed_text(query)], dtype="float32")
        query_vector = self._normalize_vectors(query_vector)
        scores, indices = self._index.search(query_vector, min(top_k, self._index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0:
                continue
            results.append({"document": self._documents[int(idx)], "score": float(score)})
        return results

    def batch_search(self, queries: list[str], top_k: int = 5) -> list[list[dict[str, Any]]]:
        return [self.search(query, top_k=top_k) for query in queries]

    def _persist(self) -> None:
        if self._index is None:
            return
        path = Path(self._index_path)
        faiss.write_index(self._index, str(path))
        path.with_suffix(".json").write_text(json.dumps(self._documents), encoding="utf-8")
