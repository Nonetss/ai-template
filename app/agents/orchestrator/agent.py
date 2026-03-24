from pydantic_ai import Agent, FunctionToolset
from core import model
from agents.example_agent.agent import example_agent


async def run_example_agent(prompt: str) -> str:
    """Delegates a task to the example agent."""
    result = await example_agent.run(prompt)
    return result.output


toolset = FunctionToolset(tools=[run_example_agent])

orchestrator = Agent(
    model,
    system_prompt=(
        "You are the main orchestrator. Delegate tasks to specialized agents "
        "based on the user's request."
    ),
    toolsets=[toolset],
)
