from agents import OrchestratorAgent, WorkerAgent
from agents.example_agent.agent import ExampleAgent


class Orchestrator(OrchestratorAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are the main orchestrator. Delegate tasks to specialized agents "
            "based on the user's request."
        )

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            ExampleAgent(name="example", description="A specialized example agent."),
        ]
