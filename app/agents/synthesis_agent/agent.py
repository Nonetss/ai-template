from agents import OrchestratorAgent, WorkerAgent
from agents.workers.search_agent.agent import SearchAgent
from agents.workers.extract_agent.agent import ExtractAgent
from tools import WorkerTool
from tools.date.datetime_tool import current_datetime_tool
from tools.redis.redis_tools import redis_get_tool, redis_keys_tool


class SynthesisAgent(OrchestratorAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert analyst and writer. Follow these steps:\n"
            "1. Use the search agent to find relevant URLs — it saves them to Redis and returns the keys.\n"
            "2. Use redis_get to retrieve the URL list from those keys.\n"
            "3. Pass the URLs directly to the extract agent to pull key information from them.\n"
            "4. Synthesize everything into a single, coherent, well-structured answer "
            "that directly addresses the question. Cite the sources.\n\n"
            "IMPORTANT: Always read the URLs from Redis yourself before calling extract. "
            "The extract agent receives URLs, not Redis keys."
        )

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            SearchAgent(
                name="search",
                description="Searches the web and returns a list of relevant URLs for a given topic.",
            ),
            ExtractAgent(
                name="extract",
                description="Extracts key information from a list of URLs relevant to the user's question.",
            ),
        ]

    @property
    def tools(self) -> list[WorkerTool]:
        return [current_datetime_tool, redis_keys_tool, redis_get_tool]


if __name__ == "__main__":
    import asyncio
    import logfire
    import os
    from core import (
        LOGFIRE_SERVICE_NAME,
        LOGFIRE_SERVICE_VERSION,
        LOGFIRE_ENVIRONMENT,
        LOGFIRE_SEND_TO_LOGFIRE,
        LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT,
    )

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT
    os.environ["OTEL_METRICS_EXPORTER"] = "none"

    logfire.configure(
        send_to_logfire=LOGFIRE_SEND_TO_LOGFIRE,
        service_name=LOGFIRE_SERVICE_NAME,
        service_version=LOGFIRE_SERVICE_VERSION,
        environment=LOGFIRE_ENVIRONMENT,
    )
    logfire.instrument_pydantic_ai()

    async def main():
        agent = SynthesisAgent()

        pregunta = (
            "Por qué el precio del oro a día de hoy está disminuyendo "
            "si actualmente hay más incertidumbre? Explica las razones "
            "y cita las fuentes relevantes."
        )
        # Sin DB — in-memory
        output, history = await agent.run(pregunta)
        print(output)

        # Continuación con historial en memoria
        followup = "¿Y qué efecto tiene esto en la plata?"
        output2, _ = await agent.run(followup, message_history=history)
        print(output2)

    asyncio.run(main())
