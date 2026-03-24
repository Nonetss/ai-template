from agents import WorkerAgent
from tools import WorkerTool
from tools.curl.extract import extract_tool


class ExtractAgent(WorkerAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at verifying and mining information from sources. "
            "You will receive a list of URLs and the user's original question. "
            "Extract the content of each URL and identify only the data, facts, "
            "and details that are directly relevant to answering the question. "
            "Return the key findings per source — do not synthesize or conclude, "
            "just extract and organize the relevant information."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [extract_tool]
