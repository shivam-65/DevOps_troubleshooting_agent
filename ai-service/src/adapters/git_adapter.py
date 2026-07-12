from src.adapters.base_adapter import BaseAdapter


class GitAdapter(BaseAdapter):
    def _endpoint(self) -> str:
        return "/api/adapters/git"

    def _source_name(self) -> str:
        return "git"
