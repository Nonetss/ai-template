from abc import ABC, abstractmethod
from pydantic import BaseModel
from pydantic_ai import Agent, FunctionToolset, ModelMessage, RunContext
from pydantic_ai.tools import Tool
from pydantic_ai.usage import UsageLimits
from core import model as default_model, compact_model as default_compact_model
from tools import WorkerTool
from repositories.conversation_repository import ConversationRepository


class WorkerAgent(ABC):
    model: str = None
    compact: bool = False
    compact_model: str = None
    request_limit: int = 25
    tool_calls_limit: int | None = None

    @property
    def instructions(self) -> str | None:
        return None

    @property
    def system_prompt(self) -> str | None:
        return None

    @property
    def tools(self) -> list[WorkerTool]:
        return []

    def __init__(self, name: str, description: str, sequential: bool = False):
        self.name = name
        self.description = description
        self.sequential = sequential
        self._agent = Agent(
            self.model or default_model,
            instructions=self.instructions,
            system_prompt=self.system_prompt or (),
            toolsets=[FunctionToolset(tools=[t.to_tool() for t in self.tools])],
        )
        if self.compact:
            self._compactor = Agent(
                self.compact_model or default_compact_model,
                system_prompt=(
                    "You are a summarizer. Condense the following tool output into a concise summary "
                    "that preserves all key facts, data points, and actionable information. "
                    "Remove redundancy, filler, and formatting noise. Be brief."
                ),
            )

    async def _compact_output(self, output: str) -> str:
        if not self.compact:
            return output
        result = await self._compactor.run(output)
        return str(result.output)

    @property
    def _usage_limits(self) -> UsageLimits:
        return UsageLimits(
            request_limit=self.request_limit,
            tool_calls_limit=self.tool_calls_limit,
        )

    async def run(self, prompt: str, deps: BaseModel | None = None) -> str:
        result = await self._agent.run(
            prompt, deps=deps, usage_limits=self._usage_limits
        )
        return await self._compact_output(str(result.output))

    def to_tool(self) -> Tool:
        async def _run(ctx: RunContext, query: str) -> str:
            result = await self._agent.run(
                query, usage=ctx.usage, deps=ctx.deps, usage_limits=self._usage_limits
            )
            return await self._compact_output(str(result.output))

        _run.__name__ = self.name
        _run.__doc__ = self.description

        return Tool(
            _run,
            takes_ctx=True,
            name=self.name,
            description=self.description,
            sequential=self.sequential,
        )


class OrchestratorAgent(ABC):
    model: str = None
    request_limit: int = 50
    tool_calls_limit: int | None = None

    @property
    def instructions(self) -> str | None:
        return None

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
            self.model or default_model,
            instructions=self.instructions,
            system_prompt=self.system_prompt or (),
            toolsets=[FunctionToolset(tools=all_tools)],
        )

    async def run(
        self,
        prompt: str,
        deps: BaseModel | None = None,
        message_history: list[ModelMessage] | None = None,
        conversation_id: str | None = None,
    ) -> tuple[str, list[ModelMessage]]:
        if conversation_id:
            message_history = await ConversationRepository.load_messages(
                conversation_id
            )

        usage_limits = UsageLimits(
            request_limit=self.request_limit,
            tool_calls_limit=self.tool_calls_limit,
        )
        result = await self._agent.run(
            prompt,
            deps=deps,
            message_history=message_history,
            usage_limits=usage_limits,
        )

        if conversation_id:
            await ConversationRepository.save_messages(
                conversation_id, result.new_messages()
            )

        return str(result.output), result.all_messages()
