from __future__ import annotations

from typing import Annotated, Any, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.models.invoice import (
    AggregationResult,
    CategorizedInvoice,
    FinalResult,
    ImageRef,
    NormalizedInvoice,
    RawInvoiceFields,
)


def _append_list(existing: list, new: list) -> list:
    return existing + new


class AgentState(TypedDict, total=False):
    # Input
    run_id: str
    folder_path: Optional[str]
    uploaded_files: list[str]
    prompt: Optional[str]

    # Processing pipeline
    image_refs: Annotated[list[ImageRef], _append_list]
    raw_extractions: Annotated[list[RawInvoiceFields], _append_list]
    normalized_invoices: Annotated[list[NormalizedInvoice], _append_list]
    categorized_invoices: Annotated[list[CategorizedInvoice], _append_list]
    aggregation: Optional[AggregationResult]
    final_result: Optional[FinalResult]

    # Agent control
    current_step: str
    steps_completed: Annotated[list[str], _append_list]
    issues: Annotated[list[str], _append_list]
    error: Optional[str]
