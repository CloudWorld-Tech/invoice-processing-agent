"""Tests for generate_report tool."""
import pytest

from src.models.invoice import (
    AggregationResult,
    CategorizedInvoice,
    CategorySpend,
    ExpenseCategory,
    ImageRef,
)
from src.tools.generate_report import generate_report


@pytest.fixture
def image_ref():
    return ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)


@pytest.fixture
def sample_data(image_ref):
    invoices = [
        CategorizedInvoice(
            vendor="Delta", invoice_date="2024-01-01", total=1250.0,
            category=ExpenseCategory.TRAVEL, confidence=0.96,
            notes="Flight", image_ref=image_ref,
        ),
        CategorizedInvoice(
            vendor="GitHub", invoice_date="2024-12-01", total=231.0,
            category=ExpenseCategory.SOFTWARE, confidence=0.98,
            notes="Subscription", image_ref=image_ref, issues=["Minor issue"],
        ),
    ]
    aggregation = AggregationResult(
        total_spend=1481.0,
        by_category=[
            CategorySpend(category=ExpenseCategory.TRAVEL, total=1250.0, count=1),
            CategorySpend(category=ExpenseCategory.SOFTWARE, total=231.0, count=1),
        ],
        invoice_count=2,
    )
    return aggregation, invoices


class TestGenerateReport:
    @pytest.mark.asyncio
    async def test_basic_report(self, sample_data):
        agg, invoices = sample_data
        result = await generate_report(agg, invoices, [])
        assert result.total_spend == 1481.0
        assert result.invoice_count == 2
        assert len(result.invoices) == 2

    @pytest.mark.asyncio
    async def test_collects_invoice_issues(self, sample_data):
        agg, invoices = sample_data
        result = await generate_report(agg, invoices, [])
        assert any("Minor issue" in i for i in result.issues_and_assumptions)

    @pytest.mark.asyncio
    async def test_includes_run_level_issues(self, sample_data):
        agg, invoices = sample_data
        result = await generate_report(agg, invoices, ["Run-level warning"])
        assert "Run-level warning" in result.issues_and_assumptions

    @pytest.mark.asyncio
    async def test_no_issues_message(self, image_ref):
        invoices = [
            CategorizedInvoice(
                vendor="Test", invoice_date="2024-01-01", total=50.0,
                category=ExpenseCategory.OTHER, confidence=0.9,
                image_ref=image_ref,
            ),
        ]
        agg = AggregationResult(
            total_spend=50.0,
            by_category=[CategorySpend(category=ExpenseCategory.OTHER, total=50.0, count=1)],
            invoice_count=1,
        )
        result = await generate_report(agg, invoices, [])
        assert any("No issues" in i or "successfully" in i for i in result.issues_and_assumptions)
