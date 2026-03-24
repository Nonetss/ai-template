from pydantic_ai import Agent, FunctionToolset
from core import model
from tools.example.tools import get_current_time

toolset = FunctionToolset(tools=[get_current_time])

example_agent = Agent(
    model,
    system_prompt="You are a specialized agent. Describe your purpose here.",
    toolsets=[toolset],
)
