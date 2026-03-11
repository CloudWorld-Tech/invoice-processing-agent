from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.llm.base import BaseLLMClient
from src.models.invoice import (
    CategorizedInvoice,
    ImageRef,
    NormalizedInvoice,
    RawInvoiceFields,
)
from src.tools.aggregate import aggregate as aggregate_tool
from src.tools.categorize import categorize_invoice as categorize_tool
from src.tools.extract_fields import extract_invoice_fields as extract_tool
from src.tools.generate_report import generate_report as report_tool
from src.tools.load_images import load_images as load_images_tool
from src.tools.normalize import normalize_invoice as normalize_tool

logger = logging.getLogger(__name__)

# Limit concurrent LLM calls to avoid rate-limit storms
_LLM_CONCURRENCY = 5


async def load_images_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Load invoice images from folder or uploaded files."""
    image_refs = await load_images_tool(
        folder_path=state.get("folder_path"),
        uploaded_files=state.get("uploaded_files"),
    )
    return {
        "image_refs": image_refs,
        "current_step": "extract",
        "steps_completed": ["load_images"],
    }


async def extract_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Extract fields from all loaded invoice images (parallel with concurrency limit)."""
    image_refs: list[ImageRef] = state.get("image_refs", [])
    prompt = state.get("prompt")

    semaphore = asyncio.Semaphore(_LLM_CONCURRENCY)

    async def _extract_one(ref: ImageRef) -> RawInvoiceFields:
        async with semaphore:
            return await extract_tool(ref, llm_client, prompt=prompt)

    extractions = await asyncio.gather(*[_extract_one(ref) for ref in image_refs])

    return {
        "raw_extractions": list(extractions),
        "current_step": "normalize",
        "steps_completed": ["extract"],
    }


async def normalize_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Normalize all raw extractions."""
    raw_extractions: list[RawInvoiceFields] = state.get("raw_extractions", [])
    image_refs: list[ImageRef] = state.get("image_refs", [])

    normalized: list[NormalizedInvoice] = []
    issues: list[str] = []

    for i, raw in enumerate(raw_extractions):
        if i < len(image_refs):
            ref = image_refs[i]
        elif image_refs:
            logger.warning("Extraction %d has no matching image ref, using last available", i)
            ref = image_refs[-1]
        else:
            logger.error("No image refs available for normalization")
            break
        result = await normalize_tool(raw, ref)
        normalized.append(result)
        issues.extend(result.issues)

    return {
        "normalized_invoices": normalized,
        "issues": issues,
        "current_step": "categorize",
        "steps_completed": ["normalize"],
    }


async def categorize_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Categorize all normalized invoices (parallel with concurrency limit)."""
    invoices: list[NormalizedInvoice] = state.get("normalized_invoices", [])
    prompt = state.get("prompt")

    semaphore = asyncio.Semaphore(_LLM_CONCURRENCY)

    async def _categorize_one(inv: NormalizedInvoice) -> CategorizedInvoice:
        async with semaphore:
            return await categorize_tool(inv, llm_client, prompt=prompt)

    categorized = await asyncio.gather(*[_categorize_one(inv) for inv in invoices])

    return {
        "categorized_invoices": list(categorized),
        "current_step": "aggregate",
        "steps_completed": ["categorize"],
    }


async def aggregate_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Aggregate categorized invoices into totals."""
    invoices: list[CategorizedInvoice] = state.get("categorized_invoices", [])
    aggregation = await aggregate_tool(invoices)

    return {
        "aggregation": aggregation,
        "current_step": "report",
        "steps_completed": ["aggregate"],
    }


async def report_node(state: dict[str, Any], llm_client: BaseLLMClient) -> dict[str, Any]:
    """Generate the final report."""
    aggregation = state.get("aggregation")
    if aggregation is None:
        logger.error("report_node called without aggregation in state")
        raise ValueError("Cannot generate report: aggregation step has not completed")

    invoices: list[CategorizedInvoice] = state.get("categorized_invoices", [])
    issues: list[str] = state.get("issues", [])

    final_result = await report_tool(aggregation, invoices, issues)

    return {
        "final_result": final_result,
        "current_step": "done",
        "steps_completed": ["report"],
    }


# Planner: decides the next step based on current state
STEP_ORDER = ["load_images", "extract", "normalize", "categorize", "aggregate", "report", "done"]


def planner_decide(state: dict[str, Any]) -> str:
    """Determine the next node to execute based on current_step."""
    current = state.get("current_step", "load_images")
    if current in STEP_ORDER:
        return current
    return "load_images"
