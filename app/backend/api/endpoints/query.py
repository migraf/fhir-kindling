from datetime import datetime

from fastapi import APIRouter, HTTPException
from fhir_kindling.fhir_query import FHIRQueryParameters
from app.backend.memory_storage import store
from app.backend.models.query import QueryResult, Query
from app.backend.models.server import Server

router = APIRouter()


@router.post("/", response_model=QueryResult)
async def run_query(parameters: FHIRQueryParameters):
    server = store.get_server_connection()
    if not server:
        raise HTTPException(status_code=400, detail="No server configured")

    query = Query(
        server=Server(api_url=server.api_address),
        query_parameters=parameters,
        start_time=datetime.now(),
    )

    print(parameters)
    try:
        response = await server.query_async(query_parameters=parameters).all()
        query.end_time = datetime.now()
        print(response)
        return QueryResult.from_query_response(query=query, response=response)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Error running query \n {e.args[0]}"
        )
