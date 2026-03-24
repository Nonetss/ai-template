from load_dotenv import load_dotenv
import os

load_dotenv()

# OpenRouter Environment Variables
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
OPENROUTE_MODEL = os.getenv("OPENROUTE_MODEL", "qwen/qwen3.5-9b")

# Logfire Environment Variables
LOGFIRE_SERVICE_NAME = os.getenv("LOGFIRE_SERVICE_NAME", "template")
LOGFIRE_SERVICE_VERSION = os.getenv("LOGFIRE_SERVICE_VERSION", "0.1.0")
LOGFIRE_ENVIRONMENT = os.getenv("LOGFIRE_ENVIRONMENT", "development")
LOGFIRE_SEND_TO_LOGFIRE = os.getenv("LOGFIRE_SEND_TO_LOGFIRE", False)
LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"
)
