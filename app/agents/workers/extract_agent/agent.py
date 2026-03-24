from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.extract import extract_tool
from tools.redis.redis_tools import redis_get_tool, redis_set_tool


class ExtractAgent(WorkerAgent):
    compact = True

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at extracting and analyzing web content. "
            "Follow these steps strictly:\n"
            "1. Use redis_get ONCE per key to retrieve the URL list.\n"
            "2. Use the extract tool to fetch the content of each URL. This is the critical step.\n"
            "3. Analyze the extracted content and keep only facts relevant to the question.\n"
            "4. Save your findings to Redis with redis_set (key: 'extract:<topic>:findings').\n"
            "5. Return the Redis keys where findings were saved.\n\n"
            "IMPORTANT: Do NOT call redis_get repeatedly on the same key. "
            "Once you have the URLs, move to step 2 immediately."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool, redis_get_tool, redis_set_tool]
