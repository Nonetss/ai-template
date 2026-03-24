from load_dotenv import load_dotenv
import os

load_dotenv()

# OpenRouter Environment Variables
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
OPENROUTE_MODEL = os.getenv("OPENROUTE_MODEL", "qwen/qwen3.5-9b")
OPENROUTE_COMPACT_MODEL = os.getenv(
    "OPENROUTE_COMPACT_MODEL", "qwen/qwen3.5-flash-02-23"
)

# Logfire Environment Variables
LOGFIRE_SERVICE_NAME = os.getenv("LOGFIRE_SERVICE_NAME", "template")
LOGFIRE_SERVICE_VERSION = os.getenv("LOGFIRE_SERVICE_VERSION", "0.1.0")
LOGFIRE_ENVIRONMENT = os.getenv("LOGFIRE_ENVIRONMENT", "development")
LOGFIRE_SEND_TO_LOGFIRE = os.getenv("LOGFIRE_SEND_TO_LOGFIRE", False)
LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"
)


# Redis Environment Variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# PostgreSQL Environment Variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://agent:agent@localhost:5432/agent"
)

# Tavily Environment Variables
TAVILY_API_BASE_URL = os.getenv("TAVILY_API_BASE_URL", "https://api.tavily.io/v1")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
