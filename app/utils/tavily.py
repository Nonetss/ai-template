from app.core.config import TAVILY_API_BASE_URL, TAVILY_API_KEY
from tavily import TavilyClient

tavily_client = TavilyClient(
    api_base_url=TAVILY_API_BASE_URL,
    api_key=TAVILY_API_KEY,
)
