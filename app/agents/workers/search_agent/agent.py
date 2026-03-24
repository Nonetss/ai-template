from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.search import search_tool
from tools.date.datetime_tool import current_datetime_tool


class SearchAgent(WorkerAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at finding relevant sources on the web. "
            "Given a topic or question, your only goal is to search and collect "
            "as many relevant URLs as possible that could help answer it. "
            "Do multiple searches with different queries to maximize coverage. "
            "Return only a list of URLs with a brief description of each — "
            "do not answer the question yourself."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_datetime_tool]
