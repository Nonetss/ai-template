from noneai import WorkerAgent, WorkerTool
from tools.curl.search import search_tool
from tools.date.datetime_tool import current_datetime_tool
from tools.redis.redis_tools import redis_set_tool, redis_keys_tool

from core.model import worker_model


class SearchAgent(WorkerAgent):
    model = worker_model

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at finding relevant sources on the web. "
            "Follow these steps:\n"
            "1. Use current_datetime to know today's date.\n"
            "2. Use the search tool with 2-3 different queries to maximize coverage.\n"
            "3. Collect all unique URLs from the results.\n"
            "4. Save the URLs as a JSON array to Redis with redis_set (key: 'search:<topic>:urls').\n"
            "5. Return the Redis keys where the URLs were saved.\n\n"
            "Do NOT return the URLs directly. Do NOT do more than 3 searches."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_datetime_tool, redis_set_tool, redis_keys_tool]
