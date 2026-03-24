from pydantic_ai import Agent
from core import (
    LOGFIRE_SERVICE_NAME,
    LOGFIRE_SERVICE_VERSION,
    LOGFIRE_ENVIRONMENT,
    LOGFIRE_SEND_TO_LOGFIRE,
    LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT,
    model,
)
import asyncio
import logfire
import os

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT
os.environ["OTEL_METRICS_EXPORTER"] = "none"

logfire.configure(
    send_to_logfire=LOGFIRE_SEND_TO_LOGFIRE,
    service_name=LOGFIRE_SERVICE_NAME,
    service_version=LOGFIRE_SERVICE_VERSION,
    environment=LOGFIRE_ENVIRONMENT,
)
logfire.instrument_pydantic_ai()

agent = Agent(model)


async def main():
    response = await agent.run("Hello, how are you?")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
