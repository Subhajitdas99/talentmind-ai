from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader


class ResumeParser:
    """Parse uploaded resume files into plain text content."""

    def __init__(self) -> None:
        self._supported_extensions = {".pdf", ".docx", ".txt"}

    def can_parse(self, filename: str) -> bool:
        return Path(filename).suffix.lower() in self._supported_extensions

    def parse(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(file_path)
        if suffix == ".docx":
            return self._parse_docx(file_path)
        if suffix == ".txt":
            return Path(file_path).read_text(encoding="utf-8")
        raise ValueError(f"Unsupported resume format: {suffix}")

    def _parse_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    def _parse_docx(self, file_path: str) -> str:
        import zipfile

        with zipfile.ZipFile(file_path) as archive:
            content = archive.read("word/document.xml").decode("utf-8")
        return content.replace("<w:p>", "\n<w:p>").replace("</w:p>", "</w:p>\n")
