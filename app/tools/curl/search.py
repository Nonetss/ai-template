from utils.tavily import tavily_client
from tools import WorkerTool
from pydantic import BaseModel
from typing import Literal, Optional


class SearchRequest(BaseModel):
    query: str
    search_depth: Literal["advanced", "basic", "fast", "ultra-fast"] = "basic"
    max_results: int = 5
    start_date: Optional[str] = None
    end_date: Optional[str] = None


def search(request: SearchRequest) -> dict:
    response = tavily_client.search(
        request.query,
        search_depth=request.search_depth,
        start_date=request.start_date,
        end_date=request.end_date,
        max_results=request.max_results,
    )
    return response


search_tool = WorkerTool(
    name="search",
    description=(
        "Search the web for up-to-date information on any topic. "
        "Use this when you need current facts, news, or data not available in your training. "
        "Returns a list of relevant results with titles, URLs, and content snippets. "
        "Prefer 'advanced' depth for complex research; 'basic' is faster for simple lookups. "
        "Use start_date/end_date (YYYY-MM-DD) to filter results by publication date."
    ),
    function=search,
    takes_ctx=False,
)


if __name__ == "__main__":
    print(search(SearchRequest(query="What is the capital of France?")))
