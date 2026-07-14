from src.state.memory_store import memory_store


class StateService:
    """Provides a clean interface over the in-memory state store."""

    def __init__(self):
        self.store = memory_store

    def get_active_scenarios(self):
        return self.store.get_active_scenarios()

    def get_active_scenarios_for_service(self, service_name: str):
        return self.store.get_active_scenarios_for_service(service_name)

    def active_scenario_count(self) -> int:
        return self.store.active_scenario_count()

    def registered_service_count(self) -> int:
        return self.store.service_registry.count()


state_service = StateService()
