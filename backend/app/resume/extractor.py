from __future__ import annotations

import re
from typing import Any


class ResumeExtractor:
    """Extract structured attributes from normalized resume text."""

    def __init__(self) -> None:
        self._skill_keywords = {
            "python",
            "fastapi",
            "sqlalchemy",
            "postgresql",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "react",
            "typescript",
            "javascript",
        }

    def extract(self, text: str) -> dict[str, Any]:
        normalized = self._normalize(text)
        return {
            "full_name": self._extract_name(normalized),
            "summary": self._extract_summary(normalized),
            "skills": self._extract_skills(normalized),
            "experience": self._extract_experience(normalized),
            "education": self._extract_education(normalized),
        }

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _extract_name(self, text: str) -> str | None:
        match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text)
        return match.group(1) if match else None

    def _extract_summary(self, text: str) -> str | None:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return sentences[0] if sentences else None

    def _extract_skills(self, text: str) -> list[str]:
        found = [skill for skill in self._skill_keywords if skill.lower() in text.lower()]
        return found

    def _extract_experience(self, text: str) -> list[str]:
        experience_lines = re.findall(r"(?:[0-9]{4}|Present|Current).{0,80}", text)
        return [line.strip() for line in experience_lines[:5]]

    def _extract_education(self, text: str) -> list[str]:
        education_matches = re.findall(r"(?:BSc|BS|BA|MS|MSc|MBA|PhD|Bachelor|Master|College|University).{0,80}", text)
        return [match.strip() for match in education_matches[:5]]
