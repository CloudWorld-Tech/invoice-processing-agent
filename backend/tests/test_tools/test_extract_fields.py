"""Tests for extract_invoice_fields tool."""
import pytest

from src.llm.mock_client import MockLLMClient
from src.models.invoice import ImageRef
from src.tools.extract_fields import _parse_total, extract_invoice_fields


@pytest.fixture
def mock_client():
    return MockLLMClient()


@pytest.fixture
def image_ref():
    return ImageRef(file_path="/tmp/test.png", file_name="test.png", index=0)


class TestExtractInvoiceFields:
    @pytest.mark.asyncio
    async def test_extract_returns_raw_fields(self, mock_client, image_ref):
        result = await extract_invoice_fields(image_ref, mock_client)
        assert result.vendor is not None
        assert result.total is not None
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_extract_with_prompt(self, mock_client, image_ref):
        result = await extract_invoice_fields(image_ref, mock_client, prompt="be conservative")
        assert result.vendor is not None


class TestParseTotal:
    def test_float_value(self):
        assert _parse_total(123.45) == 123.45

    def test_int_value(self):
        assert _parse_total(100) == 100.0

    def test_string_with_dollar(self):
        assert _parse_total("$1,250.00") == 1250.0

    def test_none_value(self):
        assert _parse_total(None) is None

    def test_invalid_string(self):
        assert _parse_total("not a number") is None
