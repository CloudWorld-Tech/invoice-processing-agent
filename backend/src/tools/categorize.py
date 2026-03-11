from __future__ import annotations

from typing import Optional

from src.llm.base import BaseLLMClient
from src.models.invoice import (
    CategorizedInvoice,
    ExpenseCategory,
    NormalizedInvoice,
)

ALLOWED_CATEGORIES = [c.value for c in ExpenseCategory]


async def categorize_invoice(
    invoice: NormalizedInvoice,
    llm_client: BaseLLMClient,
    prompt: Optional[str] = None,
) -> CategorizedInvoice:
    """Categorize a normalized invoice using the LLM."""
    result = await llm_client.categorize_invoice(
        vendor=invoice.vendor,
        total=invoice.total,
        line_items=invoice.line_items,
        allowed_categories=ALLOWED_CATEGORIES,
        prompt=prompt,
    )

    category_str = result.get("category", "Other")
    category = _match_category(category_str)
    confidence = float(result.get("confidence", 0.0))
    notes = result.get("notes")

    if category == ExpenseCategory.OTHER and not notes:
        notes = f"Could not confidently match to a specific category (raw: {category_str})"

    issues = list(invoice.issues)
    if confidence < 0.7:
        issues.append(f"Low categorization confidence: {confidence:.2f}")

    # Merge extraction flags (from earlier pipeline stages) with categorization flags
    flags = list(invoice.flags) + result.get("flags", [])

    return CategorizedInvoice(
        vendor=invoice.vendor,
        invoice_date=invoice.invoice_date,
        invoice_number=invoice.invoice_number,
        total=invoice.total,
        category=category,
        confidence=confidence,
        notes=notes,
        line_items=invoice.line_items,
        image_ref=invoice.image_ref,
        issues=issues,
        flags=flags,
    )


def _match_category(raw: str) -> ExpenseCategory:
    raw_lower = raw.lower().strip()
    for cat in ExpenseCategory:
        if cat.value.lower() == raw_lower:
            return cat
    # Fuzzy fallback
    for cat in ExpenseCategory:
        if raw_lower in cat.value.lower() or cat.value.lower() in raw_lower:
            return cat
    return ExpenseCategory.OTHER
