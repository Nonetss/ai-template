from agents import OrchestratorAgent, WorkerAgent
from agents.workers.search_agent.agent import SearchAgent
from agents.workers.extract_agent.agent import ExtractAgent
from tools import WorkerTool
from tools.date.datetime_tool import current_datetime_tool
from tools.redis.redis_tools import redis_get_tool, redis_keys_tool


class SynthesisAgent(OrchestratorAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert analyst and writer. "
            "To answer a question, first use the search agent to collect relevant URLs — "
            "it will save them to Redis and return the keys where they are stored. "
            "Then use the extract agent to pull the key information from those URLs. "
            "You have access to redis_keys (list keys by glob pattern) and redis_get (retrieve a value by key) "
            "to inspect what has been saved in Redis at any point if needed. "
            "Finally, synthesize everything into a single, coherent, well-structured answer "
            "that directly addresses the question. Cite the sources that support your conclusions."
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

    from utils.database import init_db, close_db

    async def main():
        await init_db()

        agent = SynthesisAgent()

        pregunta = (
            "Por qué el precio del oro a día de hoy está disminuyendo "
            "si actualmente hay más incertidumbre? Explica las razones "
            "y cita las fuentes relevantes."
        )
        output, conv_id = await agent.run(pregunta)
        print(output)
        print(f"\n[Conversation ID: {conv_id}]")

        # Continuación de la conversación usando el mismo conversation_id
        followup = "¿Y qué efecto tiene esto en la plata?"
        output2, conv_id = await agent.run(followup, conversation_id=conv_id)
        print(output2)

        await close_db()

    asyncio.run(main())
