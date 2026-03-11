"""Tests for aggregate tool."""
import pytest

from src.models.invoice import CategorizedInvoice, ExpenseCategory, ImageRef
from src.tools.aggregate import aggregate


@pytest.fixture
def image_ref():
    return ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)


def _make_invoice(vendor: str, total: float, category: ExpenseCategory, ref: ImageRef) -> CategorizedInvoice:
    return CategorizedInvoice(
        vendor=vendor, invoice_date="2024-01-01", total=total,
        category=category, confidence=0.95, image_ref=ref,
    )


class TestAggregate:
    @pytest.mark.asyncio
    async def test_totals(self, image_ref):
        invoices = [
            _make_invoice("A", 100.0, ExpenseCategory.TRAVEL, image_ref),
            _make_invoice("B", 200.0, ExpenseCategory.TRAVEL, image_ref),
            _make_invoice("C", 50.0, ExpenseCategory.SOFTWARE, image_ref),
        ]
        result = await aggregate(invoices)
        assert result.total_spend == 350.0
        assert result.invoice_count == 3

    @pytest.mark.asyncio
    async def test_by_category(self, image_ref):
        invoices = [
            _make_invoice("A", 100.0, ExpenseCategory.TRAVEL, image_ref),
            _make_invoice("B", 50.0, ExpenseCategory.MEALS, image_ref),
        ]
        result = await aggregate(invoices)
        cats = {c.category: c for c in result.by_category}
        assert cats[ExpenseCategory.TRAVEL].total == 100.0
        assert cats[ExpenseCategory.MEALS].total == 50.0

    @pytest.mark.asyncio
    async def test_empty_list(self, image_ref):
        result = await aggregate([])
        assert result.total_spend == 0.0
        assert result.invoice_count == 0
        assert result.by_category == []

    @pytest.mark.asyncio
    async def test_rounding(self, image_ref):
        invoices = [
            _make_invoice("A", 33.33, ExpenseCategory.OTHER, image_ref),
            _make_invoice("B", 33.33, ExpenseCategory.OTHER, image_ref),
            _make_invoice("C", 33.34, ExpenseCategory.OTHER, image_ref),
        ]
        result = await aggregate(invoices)
        assert result.total_spend == 100.0

    @pytest.mark.asyncio
    async def test_sorted_by_spend(self, image_ref):
        invoices = [
            _make_invoice("A", 50.0, ExpenseCategory.OFFICE_SUPPLIES, image_ref),
            _make_invoice("B", 500.0, ExpenseCategory.TRAVEL, image_ref),
            _make_invoice("C", 100.0, ExpenseCategory.MEALS, image_ref),
        ]
        result = await aggregate(invoices)
        totals = [c.total for c in result.by_category]
        assert totals == sorted(totals, reverse=True)
