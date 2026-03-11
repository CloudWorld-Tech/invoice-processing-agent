from __future__ import annotations

import base64
import json
import logging
import mimetypes
from typing import Any, Optional

from openai import AsyncAzureOpenAI, AsyncOpenAI

from src.config import settings
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)

# Retry configuration
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds
_REQUEST_TIMEOUT = 60.0  # seconds

# Required fields for LLM response validation
_EXTRACT_REQUIRED_FIELDS = {"vendor", "total", "confidence"}
_CATEGORIZE_REQUIRED_FIELDS = {"category", "confidence"}


class OpenAIClient(BaseLLMClient):
    """OpenAI / Azure OpenAI vision client for invoice processing."""

    def __init__(self) -> None:
        if settings.is_azure:
            # Azure OpenAI: strip trailing path segments, SDK builds the rest
            azure_endpoint = settings.openai_base_url.split("/openai")[0]
            self.client = AsyncAzureOpenAI(
                api_key=settings.openai_api_key,
                azure_endpoint=azure_endpoint,
                api_version=settings.azure_api_version,
                timeout=_REQUEST_TIMEOUT,
            )
        else:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=_REQUEST_TIMEOUT,
            )
        self.model = settings.openai_model

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return data, mime_type

    async def _call_with_retry(self, call_fn, description: str) -> Any:
        """Execute an LLM call with exponential backoff retry."""
        import asyncio

        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return await call_fn()
            except Exception as e:
                last_error = e
                if attempt < _MAX_RETRIES:
                    delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                        description, attempt, _MAX_RETRIES, e, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "%s failed after %d attempts: %s",
                        description, _MAX_RETRIES, e,
                    )
        raise last_error  # type: ignore[misc]

    @staticmethod
    def _validate_response(data: dict[str, Any], required_fields: set[str], context: str) -> dict[str, Any]:
        """Validate that LLM JSON response contains required fields."""
        missing = required_fields - set(data.keys())
        if missing:
            logger.warning("LLM response for %s missing fields %s, using defaults", context, missing)
            for field in missing:
                if field == "confidence":
                    data[field] = 0.0
                elif field == "total":
                    data[field] = 0.0
                elif field == "vendor":
                    data[field] = "Unknown"
                elif field == "category":
                    data[field] = "Other"
                else:
                    data[field] = None
        return data

    async def extract_invoice_fields(
        self, image_path: str, prompt: Optional[str] = None
    ) -> dict[str, Any]:
        image_data, mime_type = self._encode_image(image_path)

        system_prompt = (
            "You are an invoice data extraction specialist. "
            "Extract structured fields from the invoice image. "
            "Return ONLY valid JSON with these fields: "
            "vendor, invoice_date (YYYY-MM-DD), invoice_number (or null), "
            "total (numeric), line_items (array of strings), "
            "raw_text (brief summary), confidence (0-1 float)."
        )
        if prompt:
            system_prompt += f"\n\nAdditional instructions: {prompt}"

        async def _do_call():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all invoice fields from this image."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high",
                                },
                            },
                        ],
                    },
                ],
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )

        response = await self._call_with_retry(_do_call, f"extract({image_path})")
        content = response.choices[0].message.content or "{}"

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("LLM returned invalid JSON for extraction: %s", e)
            data = {}

        return self._validate_response(data, _EXTRACT_REQUIRED_FIELDS, "extraction")

    async def categorize_invoice(
        self,
        vendor: str,
        total: float,
        line_items: list[str],
        allowed_categories: list[str],
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        categories_str = "\n".join(f"- {c}" for c in allowed_categories)
        system_prompt = (
            "You are an expense categorization specialist. "
            "Categorize the invoice into exactly ONE of the allowed categories. "
            "Return ONLY valid JSON with: category (exact string from list), "
            "confidence (0-1 float), notes (brief explanation).\n\n"
            f"Allowed categories:\n{categories_str}"
        )
        if prompt:
            system_prompt += f"\n\nAdditional instructions: {prompt}"

        user_content = (
            f"Vendor: {vendor}\n"
            f"Total: ${total:.2f}\n"
            f"Line items: {', '.join(line_items)}"
        )

        async def _do_call():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,
                max_tokens=256,
                response_format={"type": "json_object"},
            )

        response = await self._call_with_retry(_do_call, f"categorize({vendor})")
        content = response.choices[0].message.content or "{}"

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("LLM returned invalid JSON for categorization: %s", e)
            data = {}

        return self._validate_response(data, _CATEGORIZE_REQUIRED_FIELDS, "categorization")
