import os
from pydantic_settings import BaseSettings
from pydantic import Field

_ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")


class Settings(BaseSettings):
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model name")
    gemini_temperature: float = Field(default=0.2)
    gemini_max_tokens: int = Field(default=4096)
    gemini_timeout: int = Field(default=120)

    backend_base_url: str = Field(default="http://localhost:8080")
    adapter_timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_backoff_base: float = Field(default=1.0)

    log_level: str = Field(default="INFO")
    port: int = Field(default=8002)

    class Config:
        env_file = _ENV_FILE
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
