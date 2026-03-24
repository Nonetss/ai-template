from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
import os
import asyncio

model = OpenRouterModel(
    "qwen/qwen3.5-9b",
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTE_API_KEY")),
)
agent = Agent(model)


async def main():
    response = await agent.run("Hello, how are you?")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
