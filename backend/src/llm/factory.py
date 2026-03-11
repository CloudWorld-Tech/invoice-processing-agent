from __future__ import annotations

import logging

from src.config import settings
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


def create_llm_client() -> BaseLLMClient:
    if settings.mock_mode:
        logger.info("Using MockLLMClient (MOCK_MODE=true)")
        from src.llm.mock_client import MockLLMClient
        return MockLLMClient()
    else:
        settings.validate_for_llm()
        logger.info("Using OpenAIClient (model=%s, azure=%s)", settings.openai_model, settings.is_azure)
        from src.llm.openai_client import OpenAIClient
        return OpenAIClient()
