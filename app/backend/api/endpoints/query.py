from fastapi import APIRouter, HTTPException
from fhir_kindling.fhir_query import FHIRQueryParameters, QueryResponse
from app.backend.memory_storage import store

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def run_query(parameters: FHIRQueryParameters):
    server = store.get_server_connection()
    if not server:
        raise HTTPException(status_code=400, detail="No server configured")
    try:
        return await server.query_async(parameters).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error running query \n {e.args[0]}")
