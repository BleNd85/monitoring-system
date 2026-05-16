from datetime import datetime
from fastapi import HTTPException
from app.db import repository


async def get_latest(agent_id: str):
    snapshot = await repository.get_latest_snapshot(agent_id)
    if not snapshot:
        raise HTTPException(404, "No metrics found")
    return snapshot


async def get_range(agent_id: str, start: datetime, end: datetime):
    if start >= end:
        raise HTTPException(400, "start must be before end")
    return await repository.get_snapshots_range(agent_id, start, end)
