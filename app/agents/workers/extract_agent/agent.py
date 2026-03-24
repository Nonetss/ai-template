from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.extract import extract_tool


class ExtractAgent(WorkerAgent):
    compact = True

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at extracting and analyzing web content. "
            "You will receive a list of URLs directly. "
            "Call the extract tool ONCE passing ALL URLs as a list — it supports multiple URLs in a single call. "
            "Do NOT call extract multiple times for individual URLs. "
            "Then analyze the extracted content and return only the key facts, data points, "
            "and details that are directly relevant to answering the question."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool]
