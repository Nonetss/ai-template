from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from core.config import (
    OPENROUTE_API_KEY,
    OPENROUTE_MODEL,
    OPENROUTE_COMPACT_MODEL,
    OPENROUTE_WORKER_MODEL,
)

_provider = OpenRouterProvider(api_key=OPENROUTE_API_KEY)

model = OpenRouterModel(OPENROUTE_MODEL, provider=_provider)
worker_model = OpenRouterModel(OPENROUTE_WORKER_MODEL, provider=_provider)
compact_model = OpenRouterModel(OPENROUTE_COMPACT_MODEL, provider=_provider)
