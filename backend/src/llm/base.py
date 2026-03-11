from __future__ import annotations

import abc
from typing import Any, Optional


class BaseLLMClient(abc.ABC):
    @abc.abstractmethod
    async def extract_invoice_fields(
        self, image_path: str, prompt: Optional[str] = None
    ) -> dict[str, Any]:
        """Send an invoice image to the vision LLM and extract structured fields."""

    @abc.abstractmethod
    async def categorize_invoice(
        self,
        vendor: str,
        total: float,
        line_items: list[str],
        allowed_categories: list[str],
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """Categorize an invoice into an expense category."""
