from fastapi import APIRouter, HTTPException

from app.backend.models.server import Server
from app.backend.memory_storage import store

router = APIRouter()


@router.get("/", response_model=Server)
def get_server_info():
    try:
        return store.get_server_config()
    except ValueError:
        raise HTTPException(status_code=404, detail="No server configured")


@router.post("/", response_model=Server)
def set_server_info(server: Server):
    print(server)
    store.set_server_config(server)
    return server
