from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.dependencies import get_candidate_service
from app.api.v1.candidates.schemas import CandidateCreate, CandidateListResponse, CandidateOut, CandidateUpdate
from app.api.v1.candidates.service import CandidateService

candidate_router = APIRouter(prefix="/candidates", tags=["candidates"])


@candidate_router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateOut:
    candidate = await service.create(payload)
    return CandidateOut(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        current_title=candidate.current_title,
        location=candidate.location,
        summary=candidate.summary,
        skills=(candidate.skills or "").split(",") if candidate.skills else [],
    )


@candidate_router.get("", response_model=CandidateListResponse)
async def list_candidates(
    service: Annotated[CandidateService, Depends(get_candidate_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    query: str | None = None,
    skill: str | None = None,
    location: str | None = None,
) -> CandidateListResponse:
    items, total = await service.list(page=page, size=size, query=query, skill=skill, location=location)
    return CandidateListResponse(
        items=[
            CandidateOut(
                id=item.id,
                full_name=item.full_name,
                email=item.email,
                phone=item.phone,
                current_title=item.current_title,
                location=item.location,
                summary=item.summary,
                skills=(item.skills or "").split(",") if item.skills else [],
            )
            for item in items
        ],
        total=total,
        page=page,
        size=size,
    )


@candidate_router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: str,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateOut:
    candidate = await service.get_by_id(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return CandidateOut(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        current_title=candidate.current_title,
        location=candidate.location,
        summary=candidate.summary,
        skills=(candidate.skills or "").split(",") if candidate.skills else [],
    )


@candidate_router.put("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: str,
    payload: CandidateUpdate,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateOut:
    candidate = await service.update(candidate_id, payload)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return CandidateOut(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        current_title=candidate.current_title,
        location=candidate.location,
        summary=candidate.summary,
        skills=(candidate.skills or "").split(",") if candidate.skills else [],
    )


@candidate_router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: str,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> Response:
    deleted = await service.delete(candidate_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
