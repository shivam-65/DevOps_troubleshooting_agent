import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from src.generators.base_generator import BaseGenerator, TimeRange
from src.models.scenario import ScenarioModel
from src.scenarios.scenario_registry import scenario_registry
from src.state.memory_store import memory_store
from src.utils.random_utils import jitter
from src.utils.time_utils import parse_step


class MetricsGenerator(BaseGenerator):

    def generate(
        self,
        services: List[str],
        time_range: TimeRange,
        active_scenarios: List[ScenarioModel],
        namespace: str = "production",
        **kwargs,
    ) -> Dict[str, Any]:
        step_str = kwargs.get("step", "1m")
        step = parse_step(step_str)
        metrics_filter = kwargs.get("metrics")

        target_services = services if services else memory_store.service_registry.get_service_names()

        timestamps = []
        t = time_range.since
        while t <= time_range.until:
            timestamps.append(t)
            t += step
        if not timestamps:
            timestamps = [time_range.since]

        midpoint_idx = len(timestamps) // 2

        cpu_series = []
        memory_series = []
        request_rate_series = []
        error_rate_series = []
        latency_p50 = []
        latency_p95 = []
        latency_p99 = []

        for svc_name in target_services:
            svc_scenarios = [s for s in active_scenarios if svc_name in s.targetServices]
            metrics_effect = None
            for sc in svc_scenarios:
                scenario_def = scenario_registry.get(sc.id)
                if scenario_def:
                    effect = scenario_def.get_effects(sc.parameters)
                    if effect.metrics:
                        metrics_effect = effect.metrics
                        break

            cpu_points = []
            mem_points = []
            rr_points = []
            er_points = []
            lp50_points = []
            lp95_points = []
            lp99_points = []

            for idx, ts in enumerate(timestamps):
                is_after_trigger = idx >= midpoint_idx
                progress = (idx - midpoint_idx) / max(len(timestamps) - midpoint_idx, 1) if is_after_trigger else 0

                # CPU
                base_cpu = jitter(40.0)
                if metrics_effect and metrics_effect.cpuSpike and is_after_trigger:
                    base_cpu = jitter(40.0 + (metrics_effect.cpuSpike - 40.0) * progress)
                cpu_points.append({"timestamp": ts.isoformat(), "value": round(base_cpu, 1)})

                # Memory
                base_mem = jitter(60.0)
                if metrics_effect and metrics_effect.memoryGrowth and is_after_trigger:
                    target = metrics_effect.memorySpike or 98.0
                    base_mem = jitter(60.0 + (target - 60.0) * progress)
                elif metrics_effect and metrics_effect.memorySpike and is_after_trigger:
                    base_mem = jitter(metrics_effect.memorySpike)
                mem_points.append({"timestamp": ts.isoformat(), "value": round(base_mem, 1)})

                # Request rate
                base_rr = jitter(150.0)
                if metrics_effect and metrics_effect.requestRateDrop and is_after_trigger:
                    base_rr = jitter(150.0 * (1 - metrics_effect.requestRateDrop * progress))
                rr_points.append({"timestamp": ts.isoformat(), "value": round(base_rr, 1)})

                # Error rate
                base_er = jitter(0.1)
                if metrics_effect and metrics_effect.errorRateSpike and is_after_trigger:
                    base_er = jitter(0.1 + (metrics_effect.errorRateSpike - 0.1) * progress)
                er_points.append({"timestamp": ts.isoformat(), "value": round(base_er, 2)})

                # Latency
                base_p50 = jitter(50.0)
                base_p95 = jitter(150.0)
                base_p99 = jitter(300.0)
                if metrics_effect and metrics_effect.latencyMultiplier and is_after_trigger:
                    mult = 1.0 + (metrics_effect.latencyMultiplier - 1.0) * progress
                    base_p50 = jitter(50.0 * mult)
                    base_p95 = jitter(150.0 * mult)
                    base_p99 = jitter(300.0 * mult)
                lp50_points.append({"timestamp": ts.isoformat(), "value": round(base_p50, 1)})
                lp95_points.append({"timestamp": ts.isoformat(), "value": round(base_p95, 1)})
                lp99_points.append({"timestamp": ts.isoformat(), "value": round(base_p99, 1)})

            cpu_series.append({"service": svc_name, "unit": "percent", "dataPoints": cpu_points})
            memory_series.append({"service": svc_name, "unit": "percent", "dataPoints": mem_points})
            request_rate_series.append({"service": svc_name, "unit": "requests_per_second", "dataPoints": rr_points})
            error_rate_series.append({"service": svc_name, "unit": "percent", "dataPoints": er_points})
            latency_p50.append({"service": svc_name, "unit": "milliseconds", "dataPoints": lp50_points})
            latency_p95.append({"service": svc_name, "unit": "milliseconds", "dataPoints": lp95_points})
            latency_p99.append({"service": svc_name, "unit": "milliseconds", "dataPoints": lp99_points})

        result: Dict[str, Any] = {}
        if not metrics_filter or "cpu" in metrics_filter:
            result["cpu"] = cpu_series
        if not metrics_filter or "memory" in metrics_filter:
            result["memory"] = memory_series
        if not metrics_filter or "request_rate" in metrics_filter:
            result["requestRate"] = request_rate_series
        if not metrics_filter or "error_rate" in metrics_filter:
            result["errorRate"] = error_rate_series
        if not metrics_filter or "latency" in metrics_filter:
            result["latency"] = {
                "p50": latency_p50,
                "p95": latency_p95,
                "p99": latency_p99,
            }

        for key in ["cpu", "memory", "requestRate", "errorRate"]:
            if key not in result:
                result[key] = []
        if "latency" not in result:
            result["latency"] = {"p50": [], "p95": [], "p99": []}

        return result
