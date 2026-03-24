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
            "Use the extract tool to fetch the content of each URL, "
            "then analyze it and return only the key facts, data points, "
            "and details that are directly relevant to answering the question."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool]
