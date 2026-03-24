from abc import ABC, abstractmethod
from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.tools import Tool
from core import model
from tools import WorkerTool


class WorkerAgent(ABC):
    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    @property
    @abstractmethod
    def tools(self) -> list[WorkerTool]: ...

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._agent = Agent(
            model,
            system_prompt=self.system_prompt,
            toolsets=[FunctionToolset(tools=[t.to_tool() for t in self.tools])],
        )

    async def run(self, prompt: str, deps=None) -> str:
        result = await self._agent.run(prompt, deps=deps)
        return str(result.output)

    def to_tool(self) -> Tool:
        async def _run(ctx: RunContext, query: str) -> str:
            result = await self._agent.run(query, usage=ctx.usage)
            return str(result.output)

        _run.__name__ = self.name
        _run.__doc__ = self.description

        return Tool(_run, takes_ctx=True, name=self.name, description=self.description)


class OrchestratorAgent(ABC):
    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    @property
    @abstractmethod
    def workers(self) -> list[WorkerAgent]: ...

    def __init__(self):
        self._agent = Agent(
            model,
            system_prompt=self.system_prompt,
            toolsets=[FunctionToolset(tools=[w.to_tool() for w in self.workers])],
        )

    async def run(self, prompt: str, deps=None) -> str:
        result = await self._agent.run(prompt, deps=deps)
        return str(result.output)
