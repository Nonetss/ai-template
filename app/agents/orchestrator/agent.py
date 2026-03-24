from agents import OrchestratorAgent, WorkerAgent
from agents.search_agent.agent import SearchAgent
from agents.extract_agent.agent import ExtractAgent


class Orchestrator(OrchestratorAgent):
    has_deps = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are the main orchestrator. Delegate tasks to specialized agents "
            "based on the user's request. "
            "Use the search agent to find information on the web. "
            "Use the extract agent when you have specific URLs and need their full content."
        )

    @property
    def workers(self) -> list[WorkerAgent]:
        return [
            SearchAgent(
                name="search",
                description="Searches the web for up-to-date information on any topic. Use this to answer questions that require current facts or research.",
            ),
            ExtractAgent(
                name="extract",
                description="Extracts the full content of one or more web pages given their URLs. Use this when you already have a URL and need its complete text.",
            ),
        ]
