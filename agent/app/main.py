import uvicorn
from app.api.routes import router
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=f"Agent {settings.AGENT_ID}")
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app"
    )
