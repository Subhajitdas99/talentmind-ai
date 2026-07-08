from app.models.domain import (
    Candidate,
    CandidateSkill,
    Embedding,
    Job,
    JobSkill,
    RankingResult,
    Recruiter,
    Resume,
    SearchHistory,
    User,
)


def test_domain_models_are_importable() -> None:
    assert Candidate.__tablename__ == "candidates"
    assert Recruiter.__tablename__ == "recruiters"
    assert Resume.__tablename__ == "resumes"
    assert Job.__tablename__ == "jobs"
    assert JobSkill.__tablename__ == "job_skills"
    assert CandidateSkill.__tablename__ == "candidate_skills"
    assert Embedding.__tablename__ == "embeddings"
    assert SearchHistory.__tablename__ == "search_history"
    assert RankingResult.__tablename__ == "ranking_results"
    assert User.__tablename__ == "users"
