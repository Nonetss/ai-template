import logfire
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel

from api.v0.router import router as v0_router
from utils.database import init_db, close_db
from core import (
    LOGFIRE_SERVICE_NAME,
    LOGFIRE_SERVICE_VERSION,
    LOGFIRE_ENVIRONMENT,
    LOGFIRE_SEND_TO_LOGFIRE,
    LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT,
)

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT
os.environ["OTEL_METRICS_EXPORTER"] = "none"

logfire.configure(
    send_to_logfire=LOGFIRE_SEND_TO_LOGFIRE,
    service_name=LOGFIRE_SERVICE_NAME,
    service_version=LOGFIRE_SERVICE_VERSION,
    environment=LOGFIRE_ENVIRONMENT,
)
logfire.instrument_pydantic_ai()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=LOGFIRE_SERVICE_NAME,
    version=LOGFIRE_SERVICE_VERSION,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.instrument_fastapi(app)

app.include_router(v0_router)


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def healthcheck():
    return HealthResponse(status="ok", version=LOGFIRE_SERVICE_VERSION)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        dark_mode=True,
    )
