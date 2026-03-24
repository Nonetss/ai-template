from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.extract import extract_tool


class ExtractAgent(WorkerAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are a web content extraction specialist. "
            "Given one or more URLs, extract their full content and return it "
            "in a clean, structured format. "
            "If asked to summarize or answer questions about the content, do so "
            "based strictly on what was extracted."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool]
