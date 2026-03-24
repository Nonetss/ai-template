from agents import WorkerAgent
from tools import WorkerTool
from tools.example.tools import current_time_tool


class ExampleAgent(WorkerAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return "You are a specialized agent. Describe your purpose here."

    @property
    def tools(self) -> list[WorkerTool]:
        return [current_time_tool]
