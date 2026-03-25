from pydantic import BaseModel, Field
from utils.redis import redis_client
from noneai import WorkerTool


DEFAULT_TTL = 1800  # 30 minutes


class SetRequest(BaseModel):
    key: str
    value: str
    ttl: int = Field(
        default=DEFAULT_TTL,
        description="Time to live in seconds. Defaults to 30 minutes.",
    )


class GetRequest(BaseModel):
    key: str


class DeleteRequest(BaseModel):
    key: str


class KeysRequest(BaseModel):
    pattern: str = Field(
        default="*",
        description="Glob-style pattern to filter keys (e.g. 'user:*', 'session:42:*').",
    )


def redis_set(request: SetRequest) -> str:
    redis_client.set(request.key, request.value, ex=request.ttl)
    return f"Saved under key '{request.key}'."


def redis_get(request: GetRequest) -> str:
    value = redis_client.get(request.key)
    if value is None:
        return f"No value found for key '{request.key}'."
    return value


def redis_delete(request: DeleteRequest) -> str:
    deleted = redis_client.delete(request.key)
    if deleted:
        return f"Deleted key '{request.key}'."
    return f"Key '{request.key}' did not exist."


def redis_keys(request: KeysRequest) -> str:
    keys = redis_client.keys(request.pattern)
    if not keys:
        return "No keys found matching the pattern."
    return "\n".join(sorted(keys))


redis_set_tool = WorkerTool(
    name="redis_set",
    description=(
        "Store any string value in Redis under a given key. "
        "Use structured key names (e.g. 'session:42:urls', 'run:abc:summary') "
        "to organize data. Optionally set a TTL in seconds."
    ),
    function=redis_set,
    takes_ctx=False,
)

redis_get_tool = WorkerTool(
    name="redis_get",
    description=(
        "Retrieve a value from Redis by key. "
        "Returns the stored string, or a not-found message if the key does not exist."
    ),
    function=redis_get,
    takes_ctx=False,
)

redis_delete_tool = WorkerTool(
    name="redis_delete",
    description="Delete a key from Redis.",
    function=redis_delete,
    takes_ctx=False,
)

redis_keys_tool = WorkerTool(
    name="redis_keys",
    description=(
        "List all Redis keys matching a glob pattern. "
        "Use '*' to list all keys, or patterns like 'session:42:*' to scope the search."
    ),
    function=redis_keys,
    takes_ctx=False,
)
