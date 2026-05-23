import logging
from app.model.metrics_schema import AgentInfo

logger = logging.getLogger(__name__)


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, AgentInfo] = {}

    def get_all(self) -> list[AgentInfo]:
        return list(self._agents.values())

    def get(self, agent_id: str) -> AgentInfo | None:
        return self._agents.get(agent_id)

    def add(self, agent: AgentInfo) -> None:
        self._agents[agent.agent_id] = agent
        logger.info(
            "Agent registered: %s at %s",
            agent.agent_id,
            agent.url,
        )

    def remove(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info("Agent removed: %s", agent_id)
            return True
        return False

    def count(self) -> int:
        return len(self._agents)


agent_registry = AgentRegistry()
