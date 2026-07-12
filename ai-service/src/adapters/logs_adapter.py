from src.adapters.base_adapter import BaseAdapter


class LogsAdapter(BaseAdapter):
    def _endpoint(self) -> str:
        return "/api/adapters/logs"

    def _source_name(self) -> str:
        return "logs"

    def _add_extra_params(self, params: dict[str, str]) -> None:
        params["level"] = "ERROR"
