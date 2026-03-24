# Agent Framework

Framework multi-agente construido sobre [pydantic-ai](https://ai.pydantic.dev/) con un patrón orquestador/workers.

## Arquitectura

```
OrchestratorAgent
├── WorkerAgent (search, extract, ...)
│   └── compact (resume output con modelo barato)
├── WorkerTool  (redis, datetime, ...)
│   └── sequential (ejecucion secuencial o paralela)
└── Conversation persistence (PostgreSQL + Tortoise ORM)
    ├── Conversation (id, title, timestamps)
    └── Message (id, role, kind, payload JSON, FK → Conversation)
```

### Clases base (`app/agents/__init__.py`)

#### `WorkerAgent`

Agente especializado en una tarea concreta. El orquestador lo invoca como si fuera una tool.

| Propiedad | Tipo | Requerida | Descripcion |
|---|---|---|---|
| `system_prompt` | `str \| None` | No | Se guarda en el historial de mensajes. |
| `instructions` | `str \| None` | No | Se inyecta en cada llamada pero NO se guarda en el historial. |
| `tools` | `list[WorkerTool]` | No | Herramientas disponibles para el agente. Default `[]`. |
| `model` | `str \| Model` | No | Modelo LLM. Default: modelo global de `core/model.py`. |
| `compact` | `bool` | No | Compacta el output antes de devolverlo al orquestador. Default `False`. |
| `compact_model` | `str \| Model` | No | Modelo para compactar. Default: `compact_model` de `core/model.py`. |

Se instancia con `name`, `description` y opcionalmente `sequential`:

```python
class SearchAgent(WorkerAgent):
    compact = True  # resume output antes de devolverlo

    @property
    def system_prompt(self) -> str:
        return "You are an expert at finding relevant sources on the web..."

    @property
    def tools(self) -> list[WorkerTool]:
        return [search_tool, current_datetime_tool]
```

#### `OrchestratorAgent`

Agente que coordina workers y tools propias. Soporta historial de mensajes y persistencia opcional.

| Propiedad | Tipo | Requerida | Descripcion |
|---|---|---|---|
| `system_prompt` | `str \| None` | No | Igual que en `WorkerAgent`. |
| `instructions` | `str \| None` | No | Igual que en `WorkerAgent`. |
| `workers` | `list[WorkerAgent]` | Si | Workers que el orquestador puede invocar. |
| `tools` | `list[WorkerTool]` | No | Tools adicionales del propio orquestador. Default `[]`. |
| `model` | `str \| Model` | No | Modelo LLM. Default: modelo global de `core/model.py`. |

Su metodo `run()` devuelve `(output, messages)`. La persistencia es opt-in via `conversation_id`:

```python
class SynthesisAgent(OrchestratorAgent):
    @property
    def system_prompt(self) -> str:
        return "You are an expert analyst and writer..."

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            SearchAgent(name="search", description="Searches the web...", sequential=True),
            ExtractAgent(name="extract", description="Extracts key info..."),
        ]
```

#### `WorkerTool` (`app/tools/__init__.py`)

Wrapper sobre `pydantic_ai.Tool` para definir herramientas de forma uniforme:

```python
redis_set_tool = WorkerTool(
    name="redis_set",
    description="Store any string value in Redis under a given key.",
    function=redis_set,
    takes_ctx=False,
    sequential=True,  # fuerza ejecucion secuencial
)
```

### `system_prompt` vs `instructions`

Ambas propiedades son opcionales. La diferencia es como se comportan con el historial de mensajes:

- **`system_prompt`**: se guarda dentro del historial. Si compartes el historial entre agentes, el system prompt del agente anterior persiste. Usar cuando quieres que el contexto se mantenga.
- **`instructions`**: se inyecta en cada llamada pero NO se guarda en el historial. Cada `run()` aplica solo las instructions del agente actual. Usar cuando cada agente debe operar con sus propias reglas sin herencia.

En la mayoria de casos `system_prompt` es suficiente. Usa `instructions` si necesitas que el prompt se reevalue limpio en cada llamada sin arrastrar contexto de agentes previos.

### Ejecucion paralela vs secuencial

Por defecto, pydantic-ai ejecuta las tools en **paralelo**. Si el modelo pide llamar a `search` y `extract` a la vez, ambas corren concurrentemente.

Para forzar ejecucion secuencial, usa `sequential=True` al instanciar un `WorkerAgent` o un `WorkerTool`:

```python
# Worker secuencial (como tool del orquestador)
SearchAgent(name="search", description="...", sequential=True)

# Tool secuencial
search_tool = WorkerTool(name="search", ..., sequential=True)
```

### Compactacion de output

Los workers pueden generar outputs muy largos que consumen el contexto del orquestador. Con `compact = True`, el output del worker se resume automaticamente con un modelo barato antes de devolverlo:

```python
class SearchAgent(WorkerAgent):
    compact = True  # activa compactacion con el modelo por defecto (OPENROUTE_COMPACT_MODEL)
```

El modelo de compactacion se configura globalmente en `OPENROUTE_COMPACT_MODEL` (env var) y se puede sobreescribir por worker con `compact_model`.

## Persistencia de conversaciones

El `OrchestratorAgent` puede persistir el historial en PostgreSQL usando Tortoise ORM. La persistencia es **opt-in**: solo se activa si se pasa `conversation_id`.

```python
agent = SynthesisAgent()

# Sin persistencia — in-memory
output, history = await agent.run("¿Por que baja el oro?")
output2, history2 = await agent.run("¿Y la plata?", message_history=history)

# Con persistencia — requiere DB
from repositories.conversation_repository import ConversationRepository
conv = await ConversationRepository.create(title="Oro y plata")
output, history = await agent.run("¿Por que baja el oro?", conversation_id=conv.id)
output2, history2 = await agent.run("¿Y la plata?", conversation_id=conv.id)
```

### Modelos (`app/models/conversation.py`)

| Modelo | Campos | Descripcion |
|---|---|---|
| `Conversation` | `id`, `title`, `created_at`, `updated_at` | Agrupa mensajes de una conversacion |
| `Message` | `id`, `conversation` (FK), `role`, `kind`, `payload` (JSON), `created_at` | Mensaje individual serializado desde pydantic-ai |

- `role`: `user` o `assistant`
- `kind`: `request` o `response` (discriminador de pydantic-ai)
- `payload`: JSON completo del `ModelMessage` (incluye parts, tool calls, etc.)

### Repository (`app/repositories/conversation_repository.py`)

| Metodo | Descripcion |
|---|---|
| `create(title?)` | Crea una conversacion nueva |
| `get(id)` | Obtiene una conversacion por ID |
| `save_messages(id, messages)` | Guarda una lista de `ModelMessage` como filas individuales |
| `load_messages(id)` | Carga y deserializa todos los mensajes de una conversacion |
| `list_all()` | Lista todas las conversaciones ordenadas por `updated_at` |
| `delete(id)` | Elimina una conversacion y sus mensajes (CASCADE) |

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
├── models/
│   └── conversation.py          # Conversation, Message (Tortoise ORM)
├── repositories/
│   └── conversation_repository.py # CRUD + save/load messages
├── core/
│   ├── config.py                # Variables de entorno (modelos, Redis, DB, Logfire, Tavily)
│   └── model.py                 # model (principal) y compact_model (compactacion)
└── utils/
    ├── database.py              # Tortoise ORM init/close
    └── redis.py                 # Redis client
```
