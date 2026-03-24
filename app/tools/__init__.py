from abc import ABC
from typing import Callable

from pydantic_ai.tools import Tool


class WorkerTool(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        takes_ctx: bool = False,
        sequential: bool = False,
    ):
        self.name = name
        self.description = description
        self.function = function
        self.takes_ctx = takes_ctx
        self.sequential = sequential

    def to_tool(self) -> Tool:
        return Tool(
            self.function,
            takes_ctx=self.takes_ctx,
            name=self.name,
            description=self.description,
            sequential=self.sequential,
        )
