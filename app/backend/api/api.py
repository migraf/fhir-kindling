from fastapi import APIRouter

from app.backend.api.endpoints import resources


api_router = APIRouter()

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
