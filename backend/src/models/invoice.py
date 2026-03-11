from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseCategory(str, Enum):
    TRAVEL = "Travel (air/hotel)"
    MEALS = "Meals & Entertainment"
    SOFTWARE = "Software / Subscriptions"
    PROFESSIONAL_SERVICES = "Professional Services"
    OFFICE_SUPPLIES = "Office Supplies"
    SHIPPING = "Shipping / Postage"
    UTILITIES = "Utilities"
    OTHER = "Other"


class ImageRef(BaseModel):
    file_path: str
    file_name: str
    index: int


class RawInvoiceFields(BaseModel):
    vendor: Optional[str] = None
    invoice_date: Optional[str] = None
    invoice_number: Optional[str] = None
    total: Optional[float] = None
    line_items: list[str] = Field(default_factory=list)
    raw_text: Optional[str] = None
    confidence: float = 0.0


class NormalizedInvoice(BaseModel):
    vendor: str
    invoice_date: str
    invoice_number: Optional[str] = None
    total: float
    line_items: list[str] = Field(default_factory=list)
    image_ref: ImageRef
    issues: list[str] = Field(default_factory=list)


class CategorizedInvoice(BaseModel):
    vendor: str
    invoice_date: str
    invoice_number: Optional[str] = None
    total: float
    category: ExpenseCategory
    confidence: float
    notes: Optional[str] = None
    line_items: list[str] = Field(default_factory=list)
    image_ref: ImageRef
    issues: list[str] = Field(default_factory=list)


class CategorySpend(BaseModel):
    category: ExpenseCategory
    total: float
    count: int


class AggregationResult(BaseModel):
    total_spend: float
    by_category: list[CategorySpend]
    invoice_count: int


class FinalResult(BaseModel):
    total_spend: float
    spend_by_category: list[CategorySpend]
    invoices: list[CategorizedInvoice]
    issues_and_assumptions: list[str]
    invoice_count: int
