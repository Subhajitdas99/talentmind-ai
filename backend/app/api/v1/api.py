from fastapi import APIRouter

from app.api.v1.auth import auth_router
from app.api.v1.candidates import candidate_router
from app.api.v1.health import health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(candidate_router)
