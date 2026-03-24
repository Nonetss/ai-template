from abc import ABC, abstractmethod
from pydantic import BaseModel
from pydantic_ai import Agent, FunctionToolset, ModelMessage, RunContext
from pydantic_ai.tools import Tool
from core import model
from tools import WorkerTool


class WorkerAgent(ABC):
    has_deps: bool = False

    @property
    @abstractmethod
    def instructions(self) -> str: ...

    @property
    def system_prompt(self) -> str | None:
        return None

    @property
    @abstractmethod
    def tools(self) -> list[WorkerTool]: ...

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._agent = Agent(
            model,
            instructions=self.instructions,
            system_prompt=self.system_prompt or (),
            toolsets=[FunctionToolset(tools=[t.to_tool() for t in self.tools])],
        )

    async def run(self, prompt: str, deps: BaseModel | None = None) -> str:
        result = await self._agent.run(prompt, deps=deps)
        return str(result.output)

    def to_tool(self) -> Tool:
        async def _run(ctx: RunContext, query: str) -> str:
            if self.has_deps:
                result = await self._agent.run(query, usage=ctx.usage, deps=ctx.deps)
            else:
                result = await self._agent.run(query, usage=ctx.usage)
            return str(result.output)

        _run.__name__ = self.name
        _run.__doc__ = self.description

        return Tool(_run, takes_ctx=True, name=self.name, description=self.description)


class OrchestratorAgent(ABC):
    has_deps: bool = False

    @property
    @abstractmethod
    def instructions(self) -> str: ...

    @property
    def system_prompt(self) -> str | None:
        return None

    @property
    @abstractmethod
    def workers(self) -> list[WorkerAgent]: ...

    @property
    def tools(self) -> list[WorkerTool]:
        return []

    def __init__(self):
        all_tools = [w.to_tool() for w in self.workers] + [
            t.to_tool() for t in self.tools
        ]
        self._agent = Agent(
            model,
            instructions=self.instructions,
            system_prompt=self.system_prompt or (),
            toolsets=[FunctionToolset(tools=all_tools)],
        )

    async def run(
        self,
        prompt: str,
        deps: BaseModel | None = None,
        message_history: list[ModelMessage] | None = None,
    ) -> tuple[str, list[ModelMessage]]:
        if self.has_deps:
            result = await self._agent.run(
                prompt, deps=deps, message_history=message_history
            )
        else:
            result = await self._agent.run(prompt, message_history=message_history)
        return str(result.output), result.all_messages()
