"""Tests for normalize_invoice tool."""
import pytest

from src.models.invoice import ImageRef, RawInvoiceFields
from src.tools.normalize import _normalize_date, _normalize_vendor, normalize_invoice


@pytest.fixture
def image_ref():
    return ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)


class TestNormalizeInvoice:
    @pytest.mark.asyncio
    async def test_normalize_valid(self, image_ref):
        raw = RawInvoiceFields(
            vendor="Acme Corp", invoice_date="2024-01-15", total=100.0, confidence=0.9,
        )
        result = await normalize_invoice(raw, image_ref)
        assert result.vendor == "Acme Corp"
        assert result.invoice_date == "2024-01-15"
        assert result.total == 100.0
        assert result.issues == []

    @pytest.mark.asyncio
    async def test_missing_vendor(self, image_ref):
        raw = RawInvoiceFields(total=50.0)
        result = await normalize_invoice(raw, image_ref)
        assert result.vendor == "Unknown Vendor"
        assert any("Vendor" in i for i in result.issues)

    @pytest.mark.asyncio
    async def test_missing_total(self, image_ref):
        raw = RawInvoiceFields(vendor="Test")
        result = await normalize_invoice(raw, image_ref)
        assert result.total == 0.0
        assert any("Total" in i for i in result.issues)

    @pytest.mark.asyncio
    async def test_negative_total(self, image_ref):
        raw = RawInvoiceFields(vendor="Test", total=-50.0)
        result = await normalize_invoice(raw, image_ref)
        assert result.total == 0.0

    @pytest.mark.asyncio
    async def test_unparseable_date(self, image_ref):
        raw = RawInvoiceFields(vendor="Test", invoice_date="garbage", total=10.0)
        result = await normalize_invoice(raw, image_ref)
        assert any("Date" in i or "date" in i for i in result.issues)


class TestNormalizeDate:
    def test_iso_format(self):
        assert _normalize_date("2024-01-15") == "2024-01-15"

    def test_us_format(self):
        assert _normalize_date("01/15/2024") == "2024-01-15"

    def test_long_format(self):
        assert _normalize_date("January 15, 2024") == "2024-01-15"

    def test_empty(self):
        assert _normalize_date("") == ""

    def test_none(self):
        assert _normalize_date(None) == ""


class TestNormalizeVendor:
    def test_strips_whitespace(self):
        assert _normalize_vendor("  Acme  Corp  ") == "Acme Corp"

    def test_none(self):
        assert _normalize_vendor(None) == ""
