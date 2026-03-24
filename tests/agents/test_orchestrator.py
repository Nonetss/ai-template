import pytest
from agents.orchestrator.agent import orchestrator


@pytest.mark.asyncio
async def test_orchestrator_runs():
    result = await orchestrator.run("Say hello")
    assert result.output is not None
