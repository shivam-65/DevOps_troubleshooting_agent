import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from src.config.defaults import COMMIT_AUTHORS, COMMIT_MESSAGE_PATTERNS, FILE_PATHS
from src.generators.base_generator import BaseGenerator, TimeRange
from src.models.scenario import ScenarioModel
from src.scenarios.scenario_registry import scenario_registry
from src.state.memory_store import memory_store
from src.utils.random_utils import random_sha, random_uuid
from src.utils.time_utils import now_utc


class GitGenerator(BaseGenerator):

    def generate(
        self,
        services: List[str],
        time_range: TimeRange,
        active_scenarios: List[ScenarioModel],
        namespace: str = "production",
        **kwargs,
    ) -> Dict[str, Any]:
        limit = int(kwargs.get("limit", 20))
        target_services = services if services else memory_store.service_registry.get_service_names()

        commits: List[Dict] = []
        deployments_list: List[Dict] = []
        rollbacks: List[Dict] = []

        duration_secs = max(1, int((time_range.until - time_range.since).total_seconds()))

        for svc_name in target_services:
            svc = memory_store.service_registry.get_service(svc_name)
            if not svc:
                continue

            svc_scenarios = [s for s in active_scenarios if svc_name in s.targetServices]
            git_effect = None
            for sc in svc_scenarios:
                scenario_def = scenario_registry.get(sc.id)
                if scenario_def:
                    effect = scenario_def.get_effects(sc.parameters)
                    if effect.git:
                        git_effect = effect.git
                        break

            svc_files = FILE_PATHS.get(svc_name, [f"src/{svc_name}/main.py"])

            num_commits = random.randint(2, 5)
            for j in range(num_commits):
                ts = time_range.since + timedelta(seconds=random.randint(0, duration_secs))
                author = random.choice(COMMIT_AUTHORS)
                sha = random_sha()

                if git_effect and git_effect.commitMessage and j == 0:
                    message = git_effect.commitMessage
                    ts = time_range.since + timedelta(seconds=int(duration_secs * 0.7))
                else:
                    msg_template = random.choice(COMMIT_MESSAGE_PATTERNS)
                    message = msg_template.format(
                        component=svc_name.replace("-", " ").title(),
                        resource=random.choice(["memory", "CPU", "connections", "batch size"]),
                        service=svc_name,
                        feature=random.choice(["caching", "logging", "metrics", "auth"]),
                        operation=random.choice(["database query", "API call", "serialization"]),
                    )

                file_path = random.choice(svc_files)
                additions = random.randint(3, 50)
                deletions = random.randint(0, 20)

                commits.append({
                    "sha": sha + "0" * (12 - len(sha)),
                    "shortSha": sha[:7],
                    "author": author["name"],
                    "authorEmail": author["email"],
                    "message": message,
                    "timestamp": ts.isoformat(),
                    "service": svc_name,
                    "filesChanged": [{
                        "path": file_path,
                        "additions": additions,
                        "deletions": deletions,
                        "changeType": "modified",
                    }],
                    "totalAdditions": additions,
                    "totalDeletions": deletions,
                })

            deploy_sha = commits[0]["sha"] if commits else random_sha()
            deploy_version = svc.version
            deploy_status = "success"

            if git_effect:
                if git_effect.newVersion:
                    deploy_version = git_effect.newVersion
                if git_effect.deploymentStatus:
                    deploy_status = git_effect.deploymentStatus

            deploy_ts = time_range.since + timedelta(seconds=int(duration_secs * 0.75))
            deployments_list.append({
                "id": f"deploy-{random_uuid()[:8]}",
                "version": deploy_version,
                "service": svc_name,
                "environment": "production",
                "timestamp": deploy_ts.isoformat(),
                "deployer": "ci-bot",
                "commitSha": deploy_sha,
                "status": deploy_status,
                "duration": "PT2M30S",
            })

            if git_effect and git_effect.rollbackReason:
                rollbacks.append({
                    "id": f"rollback-{random_uuid()[:8]}",
                    "fromVersion": deploy_version,
                    "toVersion": svc.version,
                    "service": svc_name,
                    "timestamp": (deploy_ts + timedelta(minutes=15)).isoformat(),
                    "initiator": "ops-team",
                    "reason": git_effect.rollbackReason,
                })

        commits.sort(key=lambda x: x["timestamp"], reverse=True)
        return {
            "recentCommits": commits[:limit],
            "recentDeployments": deployments_list,
            "rollbacks": rollbacks,
        }
