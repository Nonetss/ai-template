from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from app.core.config import OPENROUTE_API_KEY, OPENROUTE_MODEL

model = OpenRouterModel(
    OPENROUTE_MODEL,
    provider=OpenRouterProvider(api_key=OPENROUTE_API_KEY),
)
