"""
Demo del flujo completo: Tools → Workers → Orchestrator

Escenario: un orquestador que coordina dos workers:
  - ResearcherAgent: busca y recopila información
  - WriterAgent:     redacta contenido a partir de datos

Cada worker tiene sus propias tools. El orquestador decide
a quién delegar según el prompt del usuario.
"""

import asyncio
import logfire
import os
from datetime import datetime, timezone
from pydantic import BaseModel
from pydantic_ai import RunContext

from core import (
    LOGFIRE_SERVICE_NAME,
    LOGFIRE_SERVICE_VERSION,
    LOGFIRE_ENVIRONMENT,
    LOGFIRE_SEND_TO_LOGFIRE,
    LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT,
)
from tools import WorkerTool
from agents import WorkerAgent, OrchestratorAgent

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LOGFIRE_OTEL_EXPORTER_OTLP_ENDPOINT
os.environ["OTEL_METRICS_EXPORTER"] = "none"

logfire.configure(
    send_to_logfire=LOGFIRE_SEND_TO_LOGFIRE,
    service_name=LOGFIRE_SERVICE_NAME,
    service_version=LOGFIRE_SERVICE_VERSION,
    environment=LOGFIRE_ENVIRONMENT,
)
logfire.instrument_pydantic_ai()


# ---------------------------------------------------------------------------
# Deps (Pydantic model compartido entre workers y orquestador)
# ---------------------------------------------------------------------------


class AppDeps(BaseModel):
    user_name: str
    language: str = "es"


# ---------------------------------------------------------------------------
# Funciones de tools
# ---------------------------------------------------------------------------


def get_current_time() -> str:
    """Devuelve la hora UTC actual en formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def get_current_time_with_ctx(ctx: RunContext[AppDeps]) -> str:
    """Devuelve la hora UTC actual junto al nombre del usuario."""
    now = datetime.now(timezone.utc).isoformat()
    return f"[{ctx.deps.user_name}] {now}"


def search_web(query: str) -> str:
    """Simula una búsqueda web y devuelve resultados."""
    return f"Resultados para '{query}': [Artículo 1, Artículo 2, Artículo 3]"


def format_markdown(text: str, title: str) -> str:
    """Formatea un texto como documento Markdown con título."""
    return f"# {title}\n\n{text}"


def translate(text: str, target_language: str) -> str:
    """Simula la traducción de un texto al idioma indicado."""
    return f"[Traducido a {target_language}]: {text}"


def translate_with_ctx(ctx: RunContext[AppDeps], text: str) -> str:
    """Traduce un texto al idioma configurado en las deps del usuario."""
    return f"[Traducido a {ctx.deps.language}]: {text}"


# ---------------------------------------------------------------------------
# Tools (WorkerTool)
# ---------------------------------------------------------------------------

current_time_tool = WorkerTool(
    name="get_current_time",
    description="Devuelve la hora UTC actual.",
    function=get_current_time,
    takes_ctx=False,
)

current_time_ctx_tool = WorkerTool(
    name="get_current_time_with_ctx",
    description="Devuelve la hora UTC actual junto al nombre del usuario.",
    function=get_current_time_with_ctx,
    takes_ctx=True,
)

search_tool = WorkerTool(
    name="search_web",
    description="Realiza una búsqueda web y devuelve resultados relevantes.",
    function=search_web,
    takes_ctx=False,
)

format_tool = WorkerTool(
    name="format_markdown",
    description="Formatea un texto como documento Markdown con un título.",
    function=format_markdown,
    takes_ctx=False,
)

translate_tool = WorkerTool(
    name="translate",
    description="Traduce un texto al idioma indicado.",
    function=translate,
    takes_ctx=False,
)

translate_ctx_tool = WorkerTool(
    name="translate_with_ctx",
    description="Traduce un texto al idioma configurado en las deps del usuario.",
    function=translate_with_ctx,
    takes_ctx=True,
)


# ---------------------------------------------------------------------------
# Workers (WorkerAgent)
# ---------------------------------------------------------------------------


class ResearcherAgent(WorkerAgent):
    """Busca y recopila información. No necesita deps."""

    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "Eres un investigador experto. Tu tarea es buscar información "
            "precisa y resumirla de forma clara."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_time_tool]


class WriterAgent(WorkerAgent):
    """Redacta y formatea contenido. Usa deps para personalizar el idioma."""

    has_deps = True

    @property
    def system_prompt(self) -> str:
        return (
            "Eres un redactor experto. Tu tarea es redactar contenido claro "
            "y bien estructurado, adaptado al idioma del usuario."
        )

    @property
    def tools(self) -> list[WorkerTool]:
        return [format_tool, translate_ctx_tool, current_time_ctx_tool]


# ---------------------------------------------------------------------------
# Orchestrator (OrchestratorAgent)
# ---------------------------------------------------------------------------


class MainOrchestrator(OrchestratorAgent):
    has_deps = True

    @property
    def system_prompt(self) -> str:
        return (
            "Eres el coordinador principal. Analiza el prompt del usuario y "
            "delega la tarea al worker más adecuado: usa 'researcher' para "
            "buscar información y 'writer' para redactar o formatear contenido."
        )

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            ResearcherAgent(
                name="researcher", description="Busca y recopila información."
            ),
            WriterAgent(name="writer", description="Redacta y formatea contenido."),
        ]


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------


async def main():
    orchestrator = MainOrchestrator()
    deps = AppDeps(user_name="Carlos", language="fr")

    prompts = [
        "Busca información sobre inteligencia artificial en 2025.",
        "Redacta un resumen en markdown sobre los beneficios del open source.",
    ]

    for prompt in prompts:
        print(f"\n{'=' * 60}")
        print(f"PROMPT: {prompt}")
        print("=" * 60)
        response = await orchestrator.run(prompt, deps=deps)
        print(f"RESPUESTA:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
