from __future__ import annotations

import os
from typing import Any

import torch
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Wrapper for loading and configuring the sentence-transformer model."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.device = device or self._resolve_device()
        self._model: SentenceTransformer | None = None

    def _resolve_device(self) -> str:
        if os.getenv("CUDA_VISIBLE_DEVICES"):
            return "cuda" if torch.cuda.is_available() else "cpu"
        return "cuda" if torch.cuda.is_available() else "cpu"

    def load(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def get_model(self) -> SentenceTransformer:
        return self.load()
