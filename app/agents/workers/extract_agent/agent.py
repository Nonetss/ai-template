from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.extract import extract_tool
from tools.redis.redis_tools import redis_get_tool, redis_set_tool


class ExtractAgent(WorkerAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at verifying and mining information from sources. "
            "You will receive Redis keys pointing to URL lists saved by the search agent. "
            "Use redis_get to retrieve the URLs stored under those keys, "
            "then extract the content of each URL and identify only the data, facts, "
            "and details that are directly relevant to answering the question. "
            "Save your findings to Redis using redis_set with descriptive keys "
            "(e.g. 'extract:<topic>:findings') so results are available to the orchestrator. "
            "Return the Redis keys where findings were saved — do not return the raw content directly."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool, redis_get_tool, redis_set_tool]
