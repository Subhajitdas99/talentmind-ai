from __future__ import annotations

from typing import Any


class ExplanationService:
    """Generate candidate explanations, interview questions, and resume summaries."""

    def generate_candidate_explanation(self, candidate_profile: dict[str, Any], ranking_result: dict[str, Any]) -> dict[str, Any]:
        skills = candidate_profile.get("skills", [])
        weighted_score = ranking_result.get("weighted_score", 0.0)
        percentage = int(round(weighted_score * 100))

        strong_skills = [skill for skill in skills if skill.lower() in {"python", "nlp", "fastapi", "sqlalchemy", "docker"}]
        missing_skills = [skill for skill in ["docker", "aws", "kubernetes"] if skill.lower() not in {s.lower() for s in skills}]

        return {
            "score_percentage": percentage,
            "strengths": [f"Strong {skill.title()}" for skill in strong_skills] or ["Strong baseline profile"],
            "gaps": [f"Missing {skill.title()}" for skill in missing_skills],
            "summary": self.summarize_resume(candidate_profile),
            "interview_questions": self.generate_interview_questions(candidate_profile, strong_skills, missing_skills),
        }

    def generate_interview_questions(self, candidate_profile: dict[str, Any], strong_skills: list[str], missing_skills: list[str]) -> list[str]:
        questions = []
        if strong_skills:
            questions.append(f"Can you walk through how you applied {', '.join(strong_skills[:2])} in a real project?")
        if missing_skills:
            questions.append(f"How would you approach learning {', '.join(missing_skills[:2])} for a production environment?")
        questions.append("Describe a challenging production issue you resolved and your role in the fix.")
        return questions

    def summarize_resume(self, candidate_profile: dict[str, Any]) -> str:
        full_name = candidate_profile.get("full_name") or "Candidate"
        title = candidate_profile.get("current_title") or "Professional"
        skills = candidate_profile.get("skills", [])
        summary = candidate_profile.get("summary") or ""
        skill_text = ", ".join(skills[:5]) if skills else "diverse skill set"
        return f"{full_name} is a {title} with experience in {skill_text}. {summary}".strip()
