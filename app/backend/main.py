from typing import Optional
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.api import api_router

load_dotenv(find_dotenv())
app = FastAPI(
    title="PHT Station"
)

cache = dict()
# TODO remove full wildcard for production
origins = [
    "http://localhost:8080",
    "http://localhost:8080/",
    "http://localhost:8081",
    # "http://localhost:3000",
    # "http://localhost",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
