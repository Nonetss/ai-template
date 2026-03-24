from datetime import datetime, timezone
from tools import WorkerTool


def get_current_time() -> str:
    """Returns the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


current_time_tool = WorkerTool(
    name="get_current_time",
    description="Returns the current UTC time as an ISO 8601 string.",
    function=get_current_time,
    takes_ctx=False,
)
