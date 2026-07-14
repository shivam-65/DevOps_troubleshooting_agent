from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    backend_url: str = Field(default="http://localhost:8080", description="Spring Boot backend base URL")
    simulator_url: str = Field(default="http://localhost:8001", description="Simulator base URL")
    adapter_mode: str = Field(default="simulator", description="Adapter mode: simulator or real")
    http_timeout: int = Field(default=30, description="HTTP request timeout in seconds")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
