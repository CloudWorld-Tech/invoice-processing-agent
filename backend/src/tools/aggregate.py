from __future__ import annotations

from collections import defaultdict

from src.models.invoice import (
    AggregationResult,
    CategorizedInvoice,
    CategorySpend,
    ExpenseCategory,
)


async def aggregate(invoices: list[CategorizedInvoice]) -> AggregationResult:
    """Aggregate categorized invoices into totals. Pure Python — no LLM."""
    total_spend = 0.0
    by_category: dict[ExpenseCategory, float] = defaultdict(float)
    counts: dict[ExpenseCategory, int] = defaultdict(int)

    for inv in invoices:
        total_spend += inv.total
        by_category[inv.category] += inv.total
        counts[inv.category] += 1

    category_spends = [
        CategorySpend(
            category=cat,
            total=round(by_category[cat], 2),
            count=counts[cat],
        )
        for cat in sorted(by_category.keys(), key=lambda c: by_category[c], reverse=True)
    ]

    return AggregationResult(
        total_spend=round(total_spend, 2),
        by_category=category_spends,
        invoice_count=len(invoices),
    )
