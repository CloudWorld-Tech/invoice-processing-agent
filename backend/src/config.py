import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    mock_mode: bool = True

    # OpenAI / Azure OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    azure_api_version: str = "2024-12-01-preview"

    # Upload limits
    max_upload_size_mb: int = 50

    @property
    def is_azure(self) -> bool:
        return "azure" in self.openai_base_url

    def validate_for_llm(self) -> None:
        """Fail fast if real LLM mode is configured without credentials."""
        if not self.mock_mode and not self.openai_api_key:
            raise RuntimeError(
                "MOCK_MODE is false but OPENAI_API_KEY is not set. "
                "Set OPENAI_API_KEY in .env or enable MOCK_MODE=true."
            )

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "invoice-agent"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Startup validation
try:
    settings.validate_for_llm()
except RuntimeError as e:
    logger.warning("Startup validation: %s", e)
