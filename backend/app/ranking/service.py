from __future__ import annotations

from typing import Any

from app.embedding.service import EmbeddingService


class RankingService:
    """Rank candidates against jobs using semantic and heuristic signals."""

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self._embedding_service = embedding_service or EmbeddingService()

    def score_candidate(self, candidate_profile: dict[str, Any], job_description: str) -> dict[str, Any]:
        semantic_score = self._semantic_score(candidate_profile.get("summary", ""), job_description)
        experience_score = self._experience_score(candidate_profile.get("experience", []), job_description)
        skill_score = self._skill_score(candidate_profile.get("skills", []), job_description)
        business_score = self._business_score(candidate_profile, job_description)

        weighted_score = (
            semantic_score * 0.5
            + experience_score * 0.25
            + skill_score * 0.15
            + business_score * 0.10
        )

        return {
            "semantic_score": round(semantic_score, 4),
            "experience_score": round(experience_score, 4),
            "skill_score": round(skill_score, 4),
            "business_score": round(business_score, 4),
            "weighted_score": round(weighted_score, 4),
        }

    def _semantic_score(self, candidate_summary: str, job_description: str) -> float:
        if not candidate_summary or not job_description:
            return 0.0
        candidate_vec = self._embedding_service.embed_text(candidate_summary)
        job_vec = self._embedding_service.embed_text(job_description)
        return self._cosine_similarity(candidate_vec, job_vec)

    def _experience_score(self, experiences: list[str], job_description: str) -> float:
        if not experiences or not job_description:
            return 0.0
        matched = sum(1 for experience in experiences if any(token in experience.lower() for token in self._job_tokens(job_description)))
        return min(matched / max(len(experiences), 1), 1.0)

    def _skill_score(self, skills: list[str], job_description: str) -> float:
        if not skills or not job_description:
            return 0.0
        job_tokens = {token for token in self._job_tokens(job_description)}
        matched = sum(1 for skill in skills if skill.lower() in job_tokens)
        return matched / max(len(skills), 1)

    def _business_score(self, candidate_profile: dict[str, Any], job_description: str) -> float:
        if candidate_profile.get("location") and any(token in job_description.lower() for token in ["remote", "hybrid"]):
            return 0.8
        return 0.5

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right, strict=False))
        magnitude = (sum(a * a for a in left) ** 0.5) * (sum(b * b for b in right) ** 0.5)
        if magnitude == 0:
            return 0.0
        return dot / magnitude

    def _job_tokens(self, job_description: str) -> set[str]:
        return {token.lower() for token in job_description.replace("-", " ").split() if len(token) > 2}
