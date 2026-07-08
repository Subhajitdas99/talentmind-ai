from __future__ import annotations

from typing import Any

import numpy as np

from app.embedding.model import EmbeddingModel


class EmbeddingService:
    """Service for generating and caching sentence embeddings."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        self._model_wrapper = EmbeddingModel(model_name=model_name, device=device)
        self._cache: dict[str, list[float]] = {}

    def _get_model(self) -> Any:
        return self._model_wrapper.get_model()

    def embed_text(self, text: str) -> list[float]:
        if text in self._cache:
            return self._cache[text]
        embedding = self._get_model().encode(text, convert_to_numpy=True)
        vector = embedding.astype(float).tolist()
        self._cache[text] = vector
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        uncached: list[str] = []
        cached: list[list[float]] = []
        for text in texts:
            if text in self._cache:
                cached.append(self._cache[text])
            else:
                uncached.append(text)

        if uncached:
            embeddings = self._get_model().encode(uncached, convert_to_numpy=True, batch_size=32)
            for text, embedding in zip(uncached, embeddings, strict=False):
                vector = embedding.astype(float).tolist()
                self._cache[text] = vector
                cached.append(vector)

        return cached
