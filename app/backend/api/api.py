from fastapi import APIRouter

from app.backend.api.endpoints import query, resources, server

api_router = APIRouter()

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
api_router.include_router(server.router, prefix="/server", tags=["Server"])
api_router.include_router(query.router, prefix="/query", tags=["Query"])
