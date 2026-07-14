from src.generators.kubernetes_generator import KubernetesGenerator
from src.generators.logs_generator import LogsGenerator
from src.generators.metrics_generator import MetricsGenerator
from src.generators.git_generator import GitGenerator
from src.services.scenario_service import scenario_service
from src.services.state_service import state_service


def get_kubernetes_generator() -> KubernetesGenerator:
    return KubernetesGenerator()


def get_logs_generator() -> LogsGenerator:
    return LogsGenerator()


def get_metrics_generator() -> MetricsGenerator:
    return MetricsGenerator()


def get_git_generator() -> GitGenerator:
    return GitGenerator()


def get_scenario_service():
    return scenario_service


def get_state_service():
    return state_service
