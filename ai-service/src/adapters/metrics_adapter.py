from src.adapters.base_adapter import BaseAdapter


class MetricsAdapter(BaseAdapter):
    def _endpoint(self) -> str:
        return "/api/adapters/metrics"

    def _source_name(self) -> str:
        return "metrics"

    def _add_extra_params(self, params: dict[str, str]) -> None:
        if "since" in params:
            params["from"] = params.pop("since")
        if "until" in params:
            params["to"] = params.pop("until")
