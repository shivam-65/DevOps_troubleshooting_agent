import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from src.config.defaults import API_ENDPOINTS, LOG_MESSAGES_HEALTHY
from src.generators.base_generator import BaseGenerator, TimeRange
from src.models.scenario import ScenarioModel
from src.scenarios.scenario_registry import scenario_registry
from src.state.memory_store import memory_store
from src.utils.random_utils import random_ip, random_trace_id
from src.utils.time_utils import now_utc


class LogsGenerator(BaseGenerator):

    def generate(
        self,
        services: List[str],
        time_range: TimeRange,
        active_scenarios: List[ScenarioModel],
        namespace: str = "production",
        **kwargs,
    ) -> Dict[str, Any]:
        level_filter = kwargs.get("level")
        log_type_filter = kwargs.get("type")
        limit = int(kwargs.get("limit", 100))

        target_services = services if services else memory_store.service_registry.get_service_names()

        error_logs: List[Dict] = []
        application_logs: List[Dict] = []
        access_logs: List[Dict] = []

        duration_secs = max(1, int((time_range.until - time_range.since).total_seconds()))

        for svc_name in target_services:
            svc_scenarios = [s for s in active_scenarios if svc_name in s.targetServices]
            logs_effect = None
            for sc in svc_scenarios:
                scenario_def = scenario_registry.get(sc.id)
                if scenario_def:
                    effect = scenario_def.get_effects(sc.parameters)
                    if effect.logs:
                        logs_effect = effect.logs
                        break

            num_app_logs = min(limit // max(len(target_services), 1), 20)
            for j in range(num_app_logs):
                ts = time_range.since + timedelta(seconds=random.randint(0, duration_secs))
                level = "INFO"
                if random.random() < 0.1:
                    level = "WARN"
                msg_templates = LOG_MESSAGES_HEALTHY.get(level, LOG_MESSAGES_HEALTHY["INFO"])
                message = random.choice(msg_templates).format(
                    path=random.choice(API_ENDPOINTS),
                    key=f"cache-key-{random.randint(1, 999)}",
                    latency=random.randint(10, 200),
                    query="SELECT * FROM orders",
                    attempt=random.randint(1, 3),
                    operation="database-read",
                )
                application_logs.append({
                    "timestamp": ts.isoformat(),
                    "level": level,
                    "service": svc_name,
                    "logger": f"com.{svc_name.replace('-', '.')}.Service",
                    "message": message,
                    "stackTrace": None,
                    "threadName": f"http-nio-8080-exec-{random.randint(1, 20)}",
                    "traceId": random_trace_id(),
                })

            if logs_effect:
                num_errors = max(3, int(num_app_logs * logs_effect.errorRate))
                for j in range(num_errors):
                    ts = time_range.since + timedelta(seconds=random.randint(duration_secs // 2, duration_secs))
                    pattern = random.choice(logs_effect.errorPatterns) if logs_effect.errorPatterns else "Unknown error"
                    stack_trace = None
                    if "OutOfMemoryError" in pattern or "NullPointerException" in pattern or "Exception" in pattern:
                        stack_trace = (
                            f"{pattern}\n"
                            f"\tat com.{svc_name.replace('-', '.')}.Processor.process(Processor.java:{random.randint(50, 300)})\n"
                            f"\tat com.{svc_name.replace('-', '.')}.Controller.handle(Controller.java:{random.randint(30, 100)})"
                        )
                    error_logs.append({
                        "timestamp": ts.isoformat(),
                        "level": "ERROR",
                        "service": svc_name,
                        "logger": f"com.{svc_name.replace('-', '.')}.Processor",
                        "message": pattern,
                        "stackTrace": stack_trace,
                        "threadName": f"http-nio-8080-exec-{random.randint(1, 20)}",
                        "traceId": random_trace_id(),
                    })

            num_access = min(limit // max(len(target_services), 1), 15)
            for j in range(num_access):
                ts = time_range.since + timedelta(seconds=random.randint(0, duration_secs))
                status_code = 200
                latency = random.uniform(20, 150)
                if logs_effect and random.random() < logs_effect.errorRate:
                    status_code = random.choice([500, 502, 503])
                    latency = random.uniform(500, 5000)
                access_logs.append({
                    "timestamp": ts.isoformat(),
                    "service": svc_name,
                    "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                    "path": random.choice(API_ENDPOINTS),
                    "statusCode": status_code,
                    "latencyMs": round(latency, 1),
                    "clientIp": random_ip(),
                    "userAgent": f"{random.choice(['checkout-service', 'api-gateway', 'web-client'])}/1.0",
                })

        error_logs.sort(key=lambda x: x["timestamp"])
        application_logs.sort(key=lambda x: x["timestamp"])
        access_logs.sort(key=lambda x: x["timestamp"])

        result: Dict[str, Any] = {}
        if not log_type_filter or log_type_filter == "error":
            result["errorLogs"] = error_logs[:limit]
        else:
            result["errorLogs"] = []
        if not log_type_filter or log_type_filter == "application":
            result["applicationLogs"] = application_logs[:limit]
        else:
            result["applicationLogs"] = []
        if not log_type_filter or log_type_filter == "access":
            result["accessLogs"] = access_logs[:limit]
        else:
            result["accessLogs"] = []

        if level_filter and level_filter.upper() != "ALL":
            upper = level_filter.upper()
            result["errorLogs"] = [l for l in result.get("errorLogs", []) if l["level"] == upper]
            result["applicationLogs"] = [l for l in result.get("applicationLogs", []) if l["level"] == upper]

        return result
