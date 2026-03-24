import logfire
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

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


app = FastAPI(
    title=LOGFIRE_SERVICE_NAME,
    version=LOGFIRE_SERVICE_VERSION,
    docs_url=None,
    redoc_url=None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.instrument_fastapi(app)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        dark_mode=True,
    )
