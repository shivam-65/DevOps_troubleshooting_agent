from src.adapters.base_adapter import BaseAdapter


class KubernetesAdapter(BaseAdapter):
    def _endpoint(self) -> str:
        return "/api/adapters/kubernetes"

    def _source_name(self) -> str:
        return "kubernetes"
