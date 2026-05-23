import httpx
import logging
from fastapi import HTTPException
from app.model.metrics_schema import AgentInfo, AgentRegisterRequest, HostInfo
from app.service.agent_registry import agent_registry
from app.db import repository

logger = logging.getLogger(__name__)


async def get_all() -> list[AgentInfo]:
    return agent_registry.get_all()


async def get_by_id(agent_id: str) -> AgentInfo:
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


async def register(request: AgentRegisterRequest) -> AgentInfo:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{request.url}/api/v1/host",
                timeout=10,
            )
            response.raise_for_status()
            host_info = HostInfo(**response.json())
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to reach agent at {request.url}: {e}"
        )
    agent = AgentInfo(
        agent_id=host_info.agent_id,
        url=request.url,
        name=request.name,
    )
    await repository.save_agent(agent)
    agent_registry.add(agent)
    logger.info("Agent registered: %s", agent.agent_id)
    return agent


async def remove_by_id(agent_id: str) -> None:
    deleted = await repository.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_registry.remove(agent_id)

async def health():
    return {"status": "ok", "agents": agent_registry.count()}