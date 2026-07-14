import os


class Settings:
    def __init__(self):
        self.port: int = int(os.environ.get("PORT", "8001"))
        self.log_level: str = os.environ.get("LOG_LEVEL", "INFO")
        self.default_namespace: str = os.environ.get("DEFAULT_NAMESPACE", "production")
        self.evidence_time_range: str = os.environ.get("EVIDENCE_TIME_RANGE", "1h")
        self.metrics_step: str = os.environ.get("METRICS_STEP", "1m")
        self.enable_scheduling: bool = os.environ.get("ENABLE_SCHEDULING", "true").lower() == "true"


settings = Settings()
