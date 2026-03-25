from datetime import datetime, timezone
from noneai import WorkerTool


def get_current_datetime() -> str:
    """Returns the current date and time in UTC."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")


current_datetime_tool = WorkerTool(
    name="current_datetime",
    description=(
        "Returns the current date and time in UTC. "
        "Use this to know today's date, check what day it is, "
        "or provide time context for searches and answers."
    ),
    function=get_current_datetime,
    takes_ctx=False,
)
