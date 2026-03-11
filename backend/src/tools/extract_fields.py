from __future__ import annotations

from typing import Optional

from src.llm.base import BaseLLMClient
from src.models.invoice import ImageRef, RawInvoiceFields


async def extract_invoice_fields(
    image_ref: ImageRef,
    llm_client: BaseLLMClient,
    prompt: Optional[str] = None,
) -> RawInvoiceFields:
    """Extract structured fields from a single invoice image using the vision LLM."""
    result = await llm_client.extract_invoice_fields(
        image_path=image_ref.file_path,
        prompt=prompt,
    )

    return RawInvoiceFields(
        vendor=result.get("vendor"),
        invoice_date=result.get("invoice_date"),
        invoice_number=result.get("invoice_number"),
        total=_parse_total(result.get("total")),
        line_items=result.get("line_items", []),
        raw_text=result.get("raw_text"),
        confidence=float(result.get("confidence", 0.0)),
        flags=result.get("flags", []),
    )


def _parse_total(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None
