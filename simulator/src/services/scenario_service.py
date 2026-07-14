from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.models.scenario import AffectedEvidence, ScenarioModel
from src.scenarios.scenario_registry import scenario_registry
from src.state.memory_store import memory_store
from src.utils.random_utils import random_uuid
from src.utils.time_utils import now_utc


class ScenarioService:
    """Manages scenario lifecycle: list, activate, deactivate, custom scenarios."""

    def list_all_scenarios(self) -> List[Dict[str, Any]]:
        result = []
        for scenario_def in scenario_registry.get_all():
            active = memory_store.get_active_scenario(scenario_def.id)
            if active:
                result.append(active.model_dump())
            else:
                result.append(scenario_def.to_model().model_dump())

        for cid, custom in memory_store.custom_scenarios.items():
            if cid not in [s["id"] for s in result]:
                active = memory_store.get_active_scenario(cid)
                if active:
                    result.append(active.model_dump())
                else:
                    result.append(custom.model_dump())
        return result

    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        active = memory_store.get_active_scenario(scenario_id)
        if active:
            return active.model_dump()

        scenario_def = scenario_registry.get(scenario_id)
        if scenario_def:
            return scenario_def.to_model().model_dump()

        custom = memory_store.get_custom_scenario(scenario_id)
        if custom:
            return custom.model_dump()

        return None

    def activate_scenario(
        self, scenario_id: str, target_services: List[str], parameters: Dict[str, Any]
    ) -> Optional[ScenarioModel]:
        scenario_def = scenario_registry.get(scenario_id)
        custom = memory_store.get_custom_scenario(scenario_id)

        if not scenario_def and not custom:
            return None

        for svc in target_services:
            if not memory_store.service_registry.has_service(svc):
                raise ValueError(f"Service '{svc}' not found in service registry")

        now = now_utc()
        if scenario_def:
            model = scenario_def.to_model(target_services, parameters)
        else:
            model = custom.model_copy()
            model.targetServices = target_services
            model.parameters = parameters

        model.status = "active"
        model.activatedAt = now
        model.deactivatedAt = None

        memory_store.activate_scenario(model)
        return model

    def deactivate_scenario(self, scenario_id: str) -> Optional[ScenarioModel]:
        model = memory_store.deactivate_scenario(scenario_id)
        if model:
            model.status = "inactive"
            model.deactivatedAt = now_utc()
        return model

    def create_custom_scenario(
        self,
        name: str,
        description: str,
        target_services: List[str],
        effects: Dict[str, Any],
        duration: Optional[str] = None,
    ) -> ScenarioModel:
        slug = name.lower().replace(" ", "-")
        scenario_id = f"custom-{slug}"

        model = ScenarioModel(
            id=scenario_id,
            name=name,
            description=description,
            status="inactive",
            targetServices=target_services,
            parameters={"effects": effects, "duration": duration},
            affectedEvidence=AffectedEvidence(
                kubernetes=list(effects.get("kubernetes", {}).keys()) if effects.get("kubernetes") else [],
                logs=["error_logs"] if effects.get("logs") else [],
                metrics=list(effects.get("metrics", {}).keys()) if effects.get("metrics") else [],
                git=[],
            ),
        )
        memory_store.add_custom_scenario(model)
        return model

    def delete_custom_scenario(self, scenario_id: str) -> bool:
        return memory_store.remove_custom_scenario(scenario_id)


scenario_service = ScenarioService()
