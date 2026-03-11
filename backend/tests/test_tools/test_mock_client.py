"""Tests for the mock LLM client."""
import pytest

from src.llm.mock_client import MockLLMClient


class TestMockLLMClient:
    @pytest.fixture
    def client(self):
        return MockLLMClient()

    @pytest.mark.asyncio
    async def test_extract_returns_all_fields(self, client):
        result = await client.extract_invoice_fields("/tmp/test.png")
        assert "vendor" in result
        assert "invoice_date" in result
        assert "total" in result
        assert "line_items" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_extract_deterministic(self, client):
        """Same path should always return same result."""
        r1 = await client.extract_invoice_fields("/tmp/test.png")
        r2 = await client.extract_invoice_fields("/tmp/test.png")
        assert r1["vendor"] == r2["vendor"]
        assert r1["total"] == r2["total"]

    @pytest.mark.asyncio
    async def test_extract_different_paths_may_differ(self, client):
        r1 = await client.extract_invoice_fields("/tmp/a.png")
        r2 = await client.extract_invoice_fields("/tmp/b.png")
        # Different paths hash differently — may or may not differ
        # Just verify both return valid data
        assert r1["vendor"] is not None
        assert r2["vendor"] is not None

    @pytest.mark.asyncio
    async def test_categorize_known_vendors(self, client):
        tests = [
            ("Delta Airlines", "Travel (air/hotel)"),
            ("Marriott Hotels", "Travel (air/hotel)"),
            ("GitHub", "Software / Subscriptions"),
            ("The Capital Grille", "Meals & Entertainment"),
            ("Staples", "Office Supplies"),
        ]
        for vendor, expected_cat in tests:
            result = await client.categorize_invoice(vendor, 100.0, [], [])
            assert result["category"] == expected_cat, f"Failed for {vendor}"

    @pytest.mark.asyncio
    async def test_categorize_returns_confidence(self, client):
        result = await client.categorize_invoice("Delta", 500.0, [], [])
        assert "confidence" in result
        assert 0 < result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_categorize_returns_notes(self, client):
        result = await client.categorize_invoice("GitHub", 100.0, [], [])
        assert "notes" in result
        assert isinstance(result["notes"], str)


class TestMockFailureMode:
    """Tests for the simulated failure mode in MockLLMClient."""

    @pytest.mark.asyncio
    async def test_extract_failure_mode(self):
        client = MockLLMClient(fail_on_extract=True)
        with pytest.raises(RuntimeError, match="Mock LLM extraction failure"):
            await client.extract_invoice_fields("/tmp/test.png")

    @pytest.mark.asyncio
    async def test_categorize_failure_mode(self):
        client = MockLLMClient(fail_on_categorize=True)
        with pytest.raises(RuntimeError, match="Mock LLM categorization failure"):
            await client.categorize_invoice("Test", 100.0, [], [])

    @pytest.mark.asyncio
    async def test_extract_ok_when_failure_off(self):
        client = MockLLMClient(fail_on_extract=False)
        result = await client.extract_invoice_fields("/tmp/test.png")
        assert "vendor" in result

    @pytest.mark.asyncio
    async def test_categorize_ok_when_failure_off(self):
        client = MockLLMClient(fail_on_categorize=False)
        result = await client.categorize_invoice("Delta", 100.0, [], [])
        assert "category" in result

    @pytest.mark.asyncio
    async def test_mixed_failure_mode(self):
        """Can fail on extract but succeed on categorize."""
        client = MockLLMClient(fail_on_extract=True, fail_on_categorize=False)
        with pytest.raises(RuntimeError):
            await client.extract_invoice_fields("/tmp/test.png")
        result = await client.categorize_invoice("Delta", 100.0, [], [])
        assert result["category"] == "Travel (air/hotel)"
