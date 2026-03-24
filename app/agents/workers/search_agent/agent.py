from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.search import search_tool
from tools.date.datetime_tool import current_datetime_tool
from tools.redis.redis_tools import redis_set_tool, redis_keys_tool


class SearchAgent(WorkerAgent):
    has_deps = False

    @property
    def instructions(self) -> str:
        return (
            "You are an expert at finding relevant sources on the web. "
            "Given a topic or question, your only goal is to search and collect "
            "as many relevant URLs as possible that could help answer it. "
            "Use current_datetime to know today's date and include it in your queries when relevant. "
            "Do multiple searches with different queries to maximize coverage. "
            "Once you have collected the URLs, save them to Redis using redis_set with descriptive keys "
            "(e.g. 'search:<topic>:urls') and store a JSON array of the URLs as the value. "
            "Use redis_keys to check what has already been saved and avoid duplicates. "
            "Return the Redis keys where the URLs were saved — do not return the URLs directly."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_datetime_tool, redis_set_tool, redis_keys_tool]
