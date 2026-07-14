from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router
from src.config.settings import settings
from src.services.scheduler_service import scheduler_service
from src.state.memory_store import memory_store
from src.utils.logger import setup_logging, get_logger
from src.utils.time_utils import now_utc

setup_logging()
logger = get_logger("simulator")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Simulator starting on port {settings.port}")
    scheduler_service.start()
    yield
    logger.info("Simulator shutting down")
    scheduler_service.stop()


app = FastAPI(
    title="AI DevOps Incident Commander — Simulator",
    description="Generates realistic production failure scenarios and evidence for testing.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": now_utc().isoformat(),
        "activeScenarios": memory_store.active_scenario_count(),
        "registeredServices": memory_store.service_registry.count(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=True)
