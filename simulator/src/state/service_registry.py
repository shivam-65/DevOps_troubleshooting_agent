from typing import Dict, List, Optional

from src.config.defaults import DEFAULT_SERVICES


class ServiceDefinition:
    def __init__(self, name: str, namespace: str, replicas: int,
                 healthy_replicas: int, version: str, dependencies: List[str]):
        self.name = name
        self.namespace = namespace
        self.replicas = replicas
        self.healthy_replicas = healthy_replicas
        self.version = version
        self.dependencies = dependencies

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "namespace": self.namespace,
            "replicas": self.replicas,
            "healthyReplicas": self.healthy_replicas,
            "version": self.version,
            "dependencies": self.dependencies,
        }


class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._load_defaults()

    def _load_defaults(self):
        for svc in DEFAULT_SERVICES:
            self._services[svc["name"]] = ServiceDefinition(
                name=svc["name"],
                namespace=svc["namespace"],
                replicas=svc["replicas"],
                healthy_replicas=svc["healthyReplicas"],
                version=svc["version"],
                dependencies=svc["dependencies"],
            )

    def get_service(self, name: str) -> Optional[ServiceDefinition]:
        return self._services.get(name)

    def get_all_services(self) -> List[ServiceDefinition]:
        return list(self._services.values())

    def get_service_names(self) -> List[str]:
        return list(self._services.keys())

    def add_service(self, name: str, namespace: str, replicas: int,
                    version: str, dependencies: List[str]) -> ServiceDefinition:
        svc = ServiceDefinition(
            name=name,
            namespace=namespace,
            replicas=replicas,
            healthy_replicas=replicas,
            version=version,
            dependencies=dependencies,
        )
        self._services[name] = svc
        return svc

    def remove_service(self, name: str) -> bool:
        if name in self._services:
            del self._services[name]
            return True
        return False

    def has_service(self, name: str) -> bool:
        return name in self._services

    def count(self) -> int:
        return len(self._services)

    def filter_services(self, service_names: Optional[List[str]] = None) -> List[ServiceDefinition]:
        if not service_names:
            return self.get_all_services()
        return [s for s in self._services.values() if s.name in service_names]
