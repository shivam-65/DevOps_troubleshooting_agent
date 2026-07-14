from fastapi import APIRouter, HTTPException, Response

from src.models.requests import (
    ActivateScenarioRequest,
    CreateCustomScenarioRequest,
    CreateServiceRequest,
)
from src.services.scenario_service import scenario_service
from src.state.memory_store import memory_store
from src.utils.time_utils import now_utc

router = APIRouter(tags=["Scenarios & Services"])


# ─── Scenario Management ─────────────────────────────────────────────────────

@router.get("/api/scenarios")
async def list_scenarios():
    scenarios = scenario_service.list_all_scenarios()
    return {"scenarios": scenarios}


@router.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    scenario = scenario_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return scenario


@router.post("/api/scenarios/{scenario_id}/activate")
async def activate_scenario(scenario_id: str, body: ActivateScenarioRequest):
    try:
        model = scenario_service.activate_scenario(
            scenario_id, body.targetServices, body.parameters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not model:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    return {
        "id": model.id,
        "status": model.status,
        "targetServices": model.targetServices,
        "activatedAt": model.activatedAt.isoformat() if model.activatedAt else None,
        "message": "Scenario activated successfully",
    }


@router.post("/api/scenarios/{scenario_id}/deactivate")
async def deactivate_scenario(scenario_id: str):
    model = scenario_service.deactivate_scenario(scenario_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' is not active")

    return {
        "id": model.id,
        "status": model.status,
        "deactivatedAt": model.deactivatedAt.isoformat() if model.deactivatedAt else None,
        "message": "Scenario deactivated successfully",
    }


@router.post("/api/scenarios/custom", status_code=201)
async def create_custom_scenario(body: CreateCustomScenarioRequest):
    model = scenario_service.create_custom_scenario(
        name=body.name,
        description=body.description,
        target_services=body.targetServices,
        effects=body.effects,
        duration=body.duration,
    )
    return {
        "id": model.id,
        "name": model.name,
        "status": model.status,
        "message": "Custom scenario created successfully",
    }


@router.delete("/api/scenarios/custom/{scenario_id}", status_code=204)
async def delete_custom_scenario(scenario_id: str):
    deleted = scenario_service.delete_custom_scenario(scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Custom scenario '{scenario_id}' not found")
    return Response(status_code=204)


# ─── Service Registry ────────────────────────────────────────────────────────

@router.get("/api/services")
async def list_services():
    services = memory_store.service_registry.get_all_services()
    return {
        "services": [s.to_dict() for s in services]
    }


@router.post("/api/services", status_code=201)
async def add_service(body: CreateServiceRequest):
    if memory_store.service_registry.has_service(body.name):
        raise HTTPException(status_code=409, detail=f"Service '{body.name}' already exists")
    svc = memory_store.service_registry.add_service(
        name=body.name,
        namespace=body.namespace,
        replicas=body.replicas,
        version=body.version,
        dependencies=body.dependencies,
    )
    return svc.to_dict()


@router.delete("/api/services/{service_name}", status_code=204)
async def remove_service(service_name: str):
    removed = memory_store.service_registry.remove_service(service_name)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    return Response(status_code=204)
