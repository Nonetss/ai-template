from fastapi import APIRouter
from api.v0.endpoints import example

router = APIRouter(prefix="/v0")

router.include_router(example.router, prefix="/example", tags=["Example"])
