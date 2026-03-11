from __future__ import annotations

from src.models.invoice import (
    AggregationResult,
    CategorizedInvoice,
    FinalResult,
)


async def generate_report(
    aggregation: AggregationResult,
    invoices: list[CategorizedInvoice],
    issues: list[str],
) -> FinalResult:
    """Build the final structured output from aggregation and per-invoice data. Pure Python."""
    # Collect all issues from individual invoices + run-level issues
    all_issues = list(issues)
    for inv in invoices:
        for issue in inv.issues:
            note = f"[{inv.vendor}] {issue}"
            if note not in all_issues:
                all_issues.append(note)

    if not all_issues:
        all_issues.append("No issues detected. All invoices processed successfully.")

    # Collect all flags from individual invoices, prefixed with vendor name
    all_flags: list[str] = []
    for inv in invoices:
        for flag in inv.flags:
            prefixed = f"[{inv.vendor}] {flag}"
            if prefixed not in all_flags:
                all_flags.append(prefixed)

    return FinalResult(
        total_spend=aggregation.total_spend,
        spend_by_category=aggregation.by_category,
        invoices=invoices,
        issues_and_assumptions=all_issues,
        invoice_count=aggregation.invoice_count,
        flags=all_flags,
    )
