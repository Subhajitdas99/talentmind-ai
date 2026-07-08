from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserRole(str, Enum):
    """Portal roles for human users of the TalentMind platform."""

    ADMIN = "admin"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"
    VIEWER = "viewer"


class RecruiterStatus(str, Enum):
    """Lifecycle status for recruiter accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class CandidateStatus(str, Enum):
    """Candidate pipeline state."""

    PROSPECT = "prospect"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    HIRED = "hired"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class JobStatus(str, Enum):
    """Lifecycle state for job openings."""

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class EmbeddingKind(str, Enum):
    """Type of embedding stored for downstream search and ranking flows."""

    CANDIDATE = "candidate"
    RESUME = "resume"
    JOB = "job"
    SEARCH = "search"


class BaseModel(Base):
    """Shared base for all domain entities with audit, soft-delete, and UUID identifiers."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class User(BaseModel):
    """Application user account used for authentication and platform access."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False, validate_strings=True),
        default=UserRole.CANDIDATE,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    recruiter: Mapped["Recruiter | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="save-update, merge",
    )
    candidate: Mapped["Candidate | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="save-update, merge",
    )
    search_histories: Mapped[list["SearchHistory"]] = relationship(
        back_populates="user",
        cascade="save-update, merge",
    )

    __table_args__ = (
        CheckConstraint("char_length(email) >= 3", name="ck_users_email_length"),
        CheckConstraint("char_length(full_name) >= 2", name="ck_users_full_name_length"),
    )


class Recruiter(BaseModel):
    """Recruiter organization profile linked to a platform user."""

    __tablename__ = "recruiters"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[RecruiterStatus] = mapped_column(
        SQLEnum(RecruiterStatus, native_enum=False, validate_strings=True),
        default=RecruiterStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="recruiter")
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("char_length(company_name) >= 2", name="ck_recruiters_company_name_length"),
    )


class Candidate(BaseModel):
    """Candidate profile and pipeline state."""

    __tablename__ = "candidates"

    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    current_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(
        SQLEnum(CandidateStatus, native_enum=False, validate_strings=True),
        default=CandidateStatus.PROSPECT,
        nullable=False,
        index=True,
    )

    user: Mapped[User | None] = relationship(back_populates="candidate")
    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["CandidateSkill"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    embeddings: Mapped[list["Embedding"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    ranking_results: Mapped[list["RankingResult"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("char_length(full_name) >= 2", name="ck_candidates_full_name_length"),
        CheckConstraint("years_experience IS NULL OR years_experience >= 0", name="ck_candidates_years_experience"),
    )


class Resume(BaseModel):
    """Resume payload and metadata extracted from uploaded documents."""

    __tablename__ = "resumes"

    candidate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    candidate: Mapped[Candidate] = relationship(back_populates="resumes")
    embeddings: Mapped[list["Embedding"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("char_length(file_name) >= 3", name="ck_resumes_file_name_length"),
        Index("ix_resumes_candidate_primary", "candidate_id", "is_primary"),
    )


class Job(BaseModel):
    """Job opening and requisition metadata."""

    __tablename__ = "jobs"

    recruiter_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, native_enum=False, validate_strings=True),
        default=JobStatus.DRAFT,
        nullable=False,
        index=True,
    )

    recruiter: Mapped[Recruiter] = relationship(back_populates="jobs")
    skills: Mapped[list["JobSkill"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    embeddings: Mapped[list["Embedding"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    ranking_results: Mapped[list["RankingResult"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max", name="ck_jobs_salary_range"),
        CheckConstraint("char_length(title) >= 2", name="ck_jobs_title_length"),
    )


class JobSkill(BaseModel):
    """Skill requirements declared by a job requisition."""

    __tablename__ = "job_skills"

    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    years_required: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    job: Mapped[Job] = relationship(back_populates="skills")

    __table_args__ = (
        UniqueConstraint("job_id", "skill_name", name="uq_job_skills_job_skill"),
        CheckConstraint("char_length(skill_name) >= 2", name="ck_job_skills_skill_name_length"),
    )


class CandidateSkill(BaseModel):
    """Skill profile captured for a candidate."""

    __tablename__ = "candidate_skills"

    candidate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    candidate: Mapped[Candidate] = relationship(back_populates="skills")

    __table_args__ = (
        UniqueConstraint("candidate_id", "skill_name", name="uq_candidate_skills_candidate_skill"),
        CheckConstraint("char_length(skill_name) >= 2", name="ck_candidate_skills_skill_name_length"),
        CheckConstraint("confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)", name="ck_candidate_skills_confidence_score"),
    )


class Embedding(BaseModel):
    """Vector embeddings for candidate, resume, job, or search payloads."""

    __tablename__ = "embeddings"

    candidate_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    resume_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    job_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    embedding_type: Mapped[EmbeddingKind] = mapped_column(
        SQLEnum(EmbeddingKind, native_enum=False, validate_strings=True),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    vector: Mapped[list[float]] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    candidate: Mapped[Candidate | None] = relationship(back_populates="embeddings")
    resume: Mapped[Resume | None] = relationship(back_populates="embeddings")
    job: Mapped[Job | None] = relationship(back_populates="embeddings")

    __table_args__ = (
        CheckConstraint(
            "candidate_id IS NOT NULL OR resume_id IS NOT NULL OR job_id IS NOT NULL",
            name="ck_embeddings_target_present",
        ),
        CheckConstraint("char_length(model_name) >= 2", name="ck_embeddings_model_name_length"),
    )


class SearchHistory(BaseModel):
    """User-issued searches for candidate discovery and recommendation workflows."""

    __tablename__ = "search_history"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    filters: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped[User] = relationship(back_populates="search_histories")

    __table_args__ = (
        CheckConstraint("result_count >= 0", name="ck_search_history_result_count"),
        CheckConstraint("char_length(query_text) >= 1", name="ck_search_history_query_text"),
    )


class RankingResult(BaseModel):
    """Scored ranking between a candidate and a job requisition."""

    __tablename__ = "ranking_results"

    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped[Job] = relationship(back_populates="ranking_results")
    candidate: Mapped[Candidate] = relationship(back_populates="ranking_results")

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_ranking_results_job_candidate"),
        CheckConstraint("score >= 0", name="ck_ranking_results_score"),
        CheckConstraint("rank_position >= 1", name="ck_ranking_results_rank_position"),
    )
