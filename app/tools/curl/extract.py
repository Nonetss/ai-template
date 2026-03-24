from typing import Literal, Optional, Union
from pydantic import BaseModel, Field
from app.utils.tavily import tavily_client
from app.tools import WorkerTool


class ExtractRequest(BaseModel):
    urls: Union[str, list[str]]
    chunks_per_source: Optional[int] = Field(default=3, ge=1, le=5)
    extract_depth: Literal["basic", "advanced"] = "basic"
    include_images: bool = False


def extract(request: ExtractRequest) -> dict:
    urls = [request.urls] if isinstance(request.urls, str) else request.urls
    response = tavily_client.extract(
        urls,
        chunks_per_source=request.chunks_per_source,
        extract_depth=request.extract_depth,
        include_images=request.include_images,
        format="markdown",
    )
    return response


extract_tool = WorkerTool(
    name="extract",
    description=(
        "Extract the full content of one or more web pages given their URLs. "
        "Use this when you already know the URL and need its complete text, "
        "not just a snippet. Accepts a single URL or a list of up to 20 URLs. "
        "Use 'advanced' depth to capture tables and embedded content. "
        "Returns raw markdown content per URL."
    ),
    function=extract,
    takes_ctx=False,
)

if __name__ == "__main__":
    print(
        extract(
            ExtractRequest(
                urls="https://docs.tavily.com/documentation/api-reference/endpoint/crawl"
            )
        )
    )
