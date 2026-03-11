"""Tests for invoice data models."""
import pytest
from src.models.invoice import (
    AggregationResult,
    CategorizedInvoice,
    CategorySpend,
    ExpenseCategory,
    FinalResult,
    ImageRef,
    NormalizedInvoice,
    RawInvoiceFields,
)


class TestImageRef:
    def test_create(self):
        ref = ImageRef(file_path="/tmp/test.png", file_name="test.png", index=0)
        assert ref.file_path == "/tmp/test.png"
        assert ref.file_name == "test.png"
        assert ref.index == 0


class TestRawInvoiceFields:
    def test_defaults(self):
        raw = RawInvoiceFields()
        assert raw.vendor is None
        assert raw.total is None
        assert raw.line_items == []
        assert raw.confidence == 0.0

    def test_with_values(self):
        raw = RawInvoiceFields(
            vendor="Acme Corp",
            invoice_date="2024-01-15",
            total=100.50,
            confidence=0.95,
        )
        assert raw.vendor == "Acme Corp"
        assert raw.total == 100.50


class TestExpenseCategory:
    def test_all_categories_exist(self):
        expected = [
            "Travel (air/hotel)", "Meals & Entertainment", "Software / Subscriptions",
            "Professional Services", "Office Supplies", "Shipping / Postage",
            "Utilities", "Other",
        ]
        values = [c.value for c in ExpenseCategory]
        for e in expected:
            assert e in values

    def test_category_is_string(self):
        assert isinstance(ExpenseCategory.TRAVEL.value, str)


class TestNormalizedInvoice:
    def test_create_with_issues(self):
        ref = ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)
        inv = NormalizedInvoice(
            vendor="Test", invoice_date="2024-01-01", total=50.0,
            image_ref=ref, issues=["Missing invoice number"],
        )
        assert len(inv.issues) == 1
        assert inv.invoice_number is None


class TestCategorizedInvoice:
    def test_create(self):
        ref = ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)
        inv = CategorizedInvoice(
            vendor="Test", invoice_date="2024-01-01", total=100.0,
            category=ExpenseCategory.SOFTWARE, confidence=0.95,
            image_ref=ref,
        )
        assert inv.category == ExpenseCategory.SOFTWARE


class TestAggregationResult:
    def test_create(self):
        agg = AggregationResult(
            total_spend=500.0,
            by_category=[CategorySpend(category=ExpenseCategory.TRAVEL, total=500.0, count=2)],
            invoice_count=2,
        )
        assert agg.total_spend == 500.0
        assert len(agg.by_category) == 1


class TestFinalResult:
    def test_create(self):
        result = FinalResult(
            total_spend=500.0,
            spend_by_category=[],
            invoices=[],
            issues_and_assumptions=["All good"],
            invoice_count=0,
        )
        assert result.total_spend == 500.0
        assert result.issues_and_assumptions == ["All good"]
