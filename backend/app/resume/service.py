from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from app.resume.extractor import ResumeExtractor
from app.resume.parser import ResumeParser


class ResumeService:
    """Orchestrates resume ingestion and structured extraction."""

    def __init__(self) -> None:
        self._parser = ResumeParser()
        self._extractor = ResumeExtractor()

    def process(self, file_content: bytes, filename: str) -> dict[str, Any]:
        if not self._parser.can_parse(filename):
            raise ValueError(f"Unsupported resume format: {Path(filename).suffix}")

        with NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            raw_text = self._parser.parse(temp_path)
            extracted = self._extractor.extract(raw_text)
        finally:
            Path(temp_path).unlink(missing_ok=True)

        return {
            "raw_text": raw_text,
            "normalized_text": self._normalize_text(raw_text),
            **extracted,
        }

    def _normalize_text(self, text: str) -> str:
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())
