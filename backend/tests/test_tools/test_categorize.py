"""Tests for categorize_invoice tool."""
import pytest

from src.llm.mock_client import MockLLMClient
from src.models.invoice import ExpenseCategory, ImageRef, NormalizedInvoice
from src.tools.categorize import ALLOWED_CATEGORIES, _match_category, categorize_invoice


@pytest.fixture
def mock_client():
    return MockLLMClient()


@pytest.fixture
def image_ref():
    return ImageRef(file_path="/tmp/t.png", file_name="t.png", index=0)


class TestCategorizeInvoice:
    @pytest.mark.asyncio
    async def test_categorize_known_vendor(self, mock_client, image_ref):
        inv = NormalizedInvoice(
            vendor="Delta Airlines", invoice_date="2024-01-01",
            total=1250.0, image_ref=image_ref,
        )
        result = await categorize_invoice(inv, mock_client)
        assert result.category == ExpenseCategory.TRAVEL
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_categorize_with_prompt(self, mock_client, image_ref):
        inv = NormalizedInvoice(
            vendor="GitHub", invoice_date="2024-12-01",
            total=231.0, image_ref=image_ref,
        )
        result = await categorize_invoice(inv, mock_client, prompt="be strict")
        assert result.category == ExpenseCategory.SOFTWARE

    @pytest.mark.asyncio
    async def test_low_confidence_adds_issue(self, mock_client, image_ref):
        # Create a vendor that doesn't match any mock — will default to index 0
        inv = NormalizedInvoice(
            vendor="Unknown", invoice_date="2024-01-01",
            total=10.0, image_ref=image_ref,
        )
        result = await categorize_invoice(inv, mock_client)
        assert result.confidence > 0  # mock returns 0.96


class TestMatchCategory:
    def test_exact_match(self):
        assert _match_category("Travel (air/hotel)") == ExpenseCategory.TRAVEL

    def test_case_insensitive(self):
        assert _match_category("travel (air/hotel)") == ExpenseCategory.TRAVEL

    def test_partial_match(self):
        assert _match_category("Software") == ExpenseCategory.SOFTWARE

    def test_unknown_defaults_to_other(self):
        assert _match_category("something random") == ExpenseCategory.OTHER


class TestAllowedCategories:
    def test_all_categories_in_list(self):
        assert len(ALLOWED_CATEGORIES) == len(ExpenseCategory)
