from fastapi import APIRouter, HTTPException

from app.backend.memory_storage import store
from app.backend.models.server import Server

router = APIRouter()


@router.get("/", response_model=Server)
def get_server_info():
    try:
        return store.get_server_config()
    except ValueError:
        raise HTTPException(status_code=404, detail="No server configured")


@router.post("/", response_model=Server)
def set_server_info(server: Server):
    store.set_server_config(server)
    try:
        conn = store.get_server_connection()
        assert conn.capabilities
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Error connecting to th server \n {e.args[0]}"
        )
    return server
