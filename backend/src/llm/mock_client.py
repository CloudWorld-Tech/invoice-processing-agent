from __future__ import annotations

import hashlib
from typing import Any, Optional

from src.llm.base import BaseLLMClient

# Deterministic fixture data keyed by a hash of the filename
_MOCK_EXTRACTIONS: list[dict[str, Any]] = [
    {
        "vendor": "Delta Airlines",
        "invoice_date": "2024-11-15",
        "invoice_number": "DL-2024-78432",
        "total": 1250.00,
        "line_items": ["Round-trip flight SFO-JFK", "Seat upgrade"],
        "raw_text": "Delta Airlines - Flight Booking Confirmation",
        "confidence": 0.95,
    },
    {
        "vendor": "Marriott Hotels",
        "invoice_date": "2024-11-20",
        "invoice_number": "MH-889012",
        "total": 489.50,
        "line_items": ["2 nights - King Suite", "Room service"],
        "raw_text": "Marriott Hotels - Stay Invoice",
        "confidence": 0.92,
    },
    {
        "vendor": "GitHub",
        "invoice_date": "2024-12-01",
        "invoice_number": "GH-ENT-2024-1201",
        "total": 231.00,
        "line_items": ["GitHub Enterprise - 11 seats", "Actions minutes overage"],
        "raw_text": "GitHub Inc - Subscription Invoice",
        "confidence": 0.97,
    },
    {
        "vendor": "The Capital Grille",
        "invoice_date": "2024-12-05",
        "invoice_number": None,
        "total": 387.25,
        "line_items": ["Dinner for 4", "Wine selection", "Gratuity"],
        "raw_text": "The Capital Grille - Receipt",
        "confidence": 0.88,
    },
    {
        "vendor": "Staples",
        "invoice_date": "2024-12-10",
        "invoice_number": "STP-99201",
        "total": 142.30,
        "line_items": ["Printer paper (5 reams)", "Ink cartridges", "Binder clips"],
        "raw_text": "Staples - Office Supply Order",
        "confidence": 0.93,
    },
]

_MOCK_CATEGORIES: list[dict[str, Any]] = [
    {"category": "Travel (air/hotel)", "confidence": 0.96, "notes": "Domestic flight booking"},
    {"category": "Travel (air/hotel)", "confidence": 0.94, "notes": "Hotel accommodation"},
    {"category": "Software / Subscriptions", "confidence": 0.98, "notes": "Monthly SaaS subscription"},
    {"category": "Meals & Entertainment", "confidence": 0.91, "notes": "Client dinner - 4 attendees"},
    {"category": "Office Supplies", "confidence": 0.95, "notes": "Standard office supply restock"},
]


class MockLLMClient(BaseLLMClient):
    """Deterministic mock client that returns fixture data without any LLM calls."""

    def __init__(
        self,
        fail_on_extract: bool = False,
        fail_on_categorize: bool = False,
    ) -> None:
        self.fail_on_extract = fail_on_extract
        self.fail_on_categorize = fail_on_categorize

    def _index_for_path(self, image_path: str) -> int:
        digest = hashlib.md5(image_path.encode()).hexdigest()
        return int(digest, 16) % len(_MOCK_EXTRACTIONS)

    async def extract_invoice_fields(
        self, image_path: str, prompt: Optional[str] = None
    ) -> dict[str, Any]:
        if self.fail_on_extract:
            raise RuntimeError("Mock LLM extraction failure (simulated)")
        idx = self._index_for_path(image_path)
        data = _MOCK_EXTRACTIONS[idx].copy()
        data["flags"] = [f"[prompt] {prompt}"] if prompt else []
        return data

    async def categorize_invoice(
        self,
        vendor: str,
        total: float,
        line_items: list[str],
        allowed_categories: list[str],
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        if self.fail_on_categorize:
            raise RuntimeError("Mock LLM categorization failure (simulated)")
        # Match by vendor name to keep results consistent
        vendor_lower = vendor.lower()
        vendor_map = {
            "delta": 0,
            "marriott": 1,
            "github": 2,
            "capital grille": 3,
            "staples": 4,
        }
        idx = 0
        for key, i in vendor_map.items():
            if key in vendor_lower:
                idx = i
                break
        data = _MOCK_CATEGORIES[idx].copy()
        data["flags"] = [f"[prompt] {prompt}"] if prompt else []
        return data
