from fastapi import APIRouter

from src.api.adapter_routes import router as adapter_router
from src.api.scenario_routes import router as scenario_router

api_router = APIRouter()
api_router.include_router(adapter_router)
api_router.include_router(scenario_router)
