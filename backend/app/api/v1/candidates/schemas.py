from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CandidateBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: Annotated[str, Field(min_length=2, max_length=255)]
    email: str = Field(min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    current_title: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    summary: str | None = Field(default=None, max_length=4000)
    skills: list[str] = Field(default_factory=list)

    @field_validator("skills")
    @classmethod
    def _normalize_skills(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    current_title: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    summary: str | None = Field(default=None, max_length=4000)
    skills: list[str] | None = None

    @field_validator("skills")
    @classmethod
    def _normalize_skills(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return [item.strip() for item in value if item and item.strip()]


class CandidateOut(CandidateBase):
    id: str


class CandidateListResponse(BaseModel):
    items: list[CandidateOut]
    total: int
    page: int
    size: int
