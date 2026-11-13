import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Automatically locate and load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class BifrostConfig(BaseModel):
    """
    Configuration model for the Bifrost LLM Gateway.
    All properties are loaded from environment variables to prevent hardcoding.
    """
    base_url: str = Field(
        default_factory=lambda: os.getenv("BIFROST_BASE_URL", "http://localhost:8080/v1").rstrip("/")
    )
    api_key: str = Field(
        default_factory=lambda: os.getenv("BIFROST_API_KEY", "bifrost-default-key")
    )
    model: str = Field(
        default_factory=lambda: os.getenv("BIFROST_MODEL", "openai/gpt-4o-mini")
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("BIFROST_TIMEOUT", "45.0"))
    )
    demo_mode: str = Field(
        default_factory=lambda: os.getenv("DEMO_MODE", "auto").lower()
    )

    def is_configured(self) -> bool:
        """Returns True if the user has provided valid Bifrost URL and non-placeholder API key."""
        return bool(
            self.base_url
            and self.api_key
            and self.api_key not in ("your_bifrost_key", "your_bifrost_api_key_here", "")
        )

    def get_health_url(self) -> str:
        """Derive standard Bifrost health endpoint from base URL."""
        # Typically base_url is http://localhost:8080/v1 -> health is http://localhost:8080/health or /healthz
        clean_base = self.base_url
        if clean_base.endswith("/v1"):
            clean_base = clean_base[:-3]
        return f"{clean_base}/health"

    def get_models_url(self) -> str:
        """Get the OpenAI-compatible /v1/models endpoint."""
        clean_base = self.base_url
        if not clean_base.endswith("/v1"):
            clean_base = f"{clean_base}/v1"
        return f"{clean_base}/models"


def get_config() -> BifrostConfig:
    return BifrostConfig()
