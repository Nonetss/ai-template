# Agent Framework

Framework multi-agente construido sobre [pydantic-ai](https://ai.pydantic.dev/) con un patrón orquestador/workers.

## Arquitectura

```
OrchestratorAgent
├── WorkerAgent (search, extract, ...)
├── WorkerTool  (redis, datetime, ...)
└── message_history (conversaciones multi-turno)
```

### Clases base (`app/agents/__init__.py`)

#### `WorkerAgent`

Agente especializado en una tarea concreta. El orquestador lo invoca como si fuera una tool.

| Propiedad | Tipo | Requerida | Descripcion |
|---|---|---|---|
| `system_prompt` | `str \| None` | No | Se guarda en el historial de mensajes. Persiste si se comparte el historial entre agentes. |
| `instructions` | `str \| None` | No | Se inyecta en cada llamada al modelo pero NO se guarda en el historial. |
| `tools` | `list[WorkerTool]` | Si | Herramientas disponibles para el agente. |
| `has_deps` | `bool` | No | Si el agente necesita dependencias (`deps`) inyectadas via `RunContext`. Default `False`. |

Se instancia con `name` y `description`, que son los que ve el orquestador al llamarlo como tool:

```python
class SearchAgent(WorkerAgent):
    @property
    def system_prompt(self) -> str:
        return "You are an expert at finding relevant sources on the web..."

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_datetime_tool]
```

#### `OrchestratorAgent`

Agente que coordina workers y tools propias. Soporta historial de mensajes para conversaciones multi-turno.

| Propiedad | Tipo | Requerida | Descripcion |
|---|---|---|---|
| `system_prompt` | `str \| None` | No | Igual que en `WorkerAgent`. |
| `instructions` | `str \| None` | No | Igual que en `WorkerAgent`. |
| `workers` | `list[WorkerAgent]` | Si | Workers que el orquestador puede invocar. |
| `tools` | `list[WorkerTool]` | No | Tools adicionales del propio orquestador. Default `[]`. |
| `has_deps` | `bool` | No | Default `False`. |

Su metodo `run()` devuelve una tupla `(output, messages)` para poder encadenar conversaciones:

```python
class SynthesisAgent(OrchestratorAgent):
    @property
    def system_prompt(self) -> str:
        return "You are an expert analyst and writer..."

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            SearchAgent(name="search", description="Searches the web..."),
            ExtractAgent(name="extract", description="Extracts key info..."),
        ]

    @property
    def tools(self) -> list[WorkerTool]:
        return [current_datetime_tool, redis_keys_tool, redis_get_tool]
```

#### `WorkerTool` (`app/tools/__init__.py`)

Wrapper sobre `pydantic_ai.Tool` para definir herramientas de forma uniforme:

```python
redis_set_tool = WorkerTool(
    name="redis_set",
    description="Store any string value in Redis under a given key.",
    function=redis_set,
    takes_ctx=False,
)
```

### `system_prompt` vs `instructions`

Ambas propiedades son opcionales. La diferencia es como se comportan con el historial de mensajes:

- **`system_prompt`**: se guarda dentro del historial. Si compartes el historial entre agentes, el system prompt del agente anterior persiste. Usar cuando quieres que el contexto se mantenga.
- **`instructions`**: se inyecta en cada llamada pero NO se guarda en el historial. Cada `run()` aplica solo las instructions del agente actual. Usar cuando cada agente debe operar con sus propias reglas sin herencia.

En la mayoria de casos `system_prompt` es suficiente. Usa `instructions` si necesitas que el prompt se reevalue limpio en cada llamada sin arrastrar contexto de agentes previos.

## Historial de mensajes

El `OrchestratorAgent` soporta conversaciones multi-turno pasando el historial entre llamadas:

```python
agent = SynthesisAgent()

# Primera pregunta
output, history = await agent.run("¿Por que baja el oro?")

# Siguiente pregunta con contexto de la anterior
output2, history2 = await agent.run("¿Y la plata?", message_history=history)
```

## Estructura del proyecto

```
app/
├── agents/
│   ├── __init__.py              # WorkerAgent, OrchestratorAgent
│   ├── synthesis_agent/
│   │   └── agent.py             # SynthesisAgent (orquestador)
│   └── workers/
│       ├── search_agent/
│       │   └── agent.py         # SearchAgent
│       └── extract_agent/
│           └── agent.py         # ExtractAgent
├── tools/
│   ├── __init__.py              # WorkerTool
│   ├── date/
│   │   └── datetime_tool.py     # current_datetime_tool
│   ├── curl/
│   │   ├── search.py            # search_tool
│   │   └── extract.py           # extract_tool
│   └── redis/
│       └── redis_tools.py       # redis_set, redis_get, redis_delete, redis_keys
├── core/
│   └── config.py                # Modelo, Redis URL, Logfire config
└── utils/
    └── redis.py                 # Redis client
```
