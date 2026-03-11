from __future__ import annotations

import re
from datetime import datetime

from src.models.invoice import ImageRef, NormalizedInvoice, RawInvoiceFields


async def normalize_invoice(
    raw: RawInvoiceFields,
    image_ref: ImageRef,
) -> NormalizedInvoice:
    """Normalize raw extracted fields into a clean, consistent format. Pure Python — no LLM."""
    issues: list[str] = []

    vendor = _normalize_vendor(raw.vendor)
    if not vendor:
        vendor = "Unknown Vendor"
        issues.append("Vendor name could not be determined")

    invoice_date = _normalize_date(raw.invoice_date)
    if not invoice_date:
        invoice_date = datetime.now().strftime("%Y-%m-%d")
        issues.append(f"Date could not be parsed from '{raw.invoice_date}'; defaulted to today")

    total = raw.total if raw.total is not None and raw.total >= 0 else 0.0
    if raw.total is None:
        issues.append("Total amount missing; defaulted to 0.00")
    elif raw.total < 0:
        issues.append(f"Negative total ({raw.total}); defaulted to 0.00")

    return NormalizedInvoice(
        vendor=vendor,
        invoice_date=invoice_date,
        invoice_number=raw.invoice_number,
        total=round(total, 2),
        line_items=raw.line_items,
        image_ref=image_ref,
        issues=issues,
        flags=raw.flags,
    )


def _normalize_vendor(vendor: str | None) -> str:
    if not vendor:
        return ""
    cleaned = vendor.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _normalize_date(date_str: str | None) -> str:
    if not date_str:
        return ""
    date_str = date_str.strip()

    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""
