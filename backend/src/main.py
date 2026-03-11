from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sse_starlette.sse import EventSourceResponse

from src.agent.graph import compile_graph
from src.config import settings
from src.llm.factory import create_llm_client
from src.models.events import SSEEventType
from src.models.requests import RunRequest
from src.streaming.sse import (
    error_event,
    final_result_event,
    format_sse,
    invoice_result_event,
    progress_event,
    run_started_event,
    tool_call_event,
    tool_result_event,
)
from src.tracing.tracer import RunTracer

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024

app = FastAPI(
    title="Invoice Processing Agent",
    description="Local invoice-processing agent with SSE streaming",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode,
        "model": settings.openai_model,
    }


@app.post("/runs/stream")
async def runs_stream(request: Request):
    """Start an invoice-processing run and stream SSE events."""
    content_type = request.headers.get("content-type", "")
    folder_path: str | None = None
    prompt: str | None = None
    files: list[UploadFile] = []

    if "application/json" in content_type:
        try:
            body = await request.json()
            req = RunRequest(**body)
            folder_path = req.folder_path
            prompt = req.prompt
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON body: %s", e)
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON. Expected: {\"folder_path\": \"...\", \"prompt\": \"...\"}"},
            )
        except (ValidationError, ValueError) as e:
            logger.warning("Request validation failed: %s", e)
            return JSONResponse(
                status_code=400,
                content={"error": f"Validation error: {e}"},
            )
    elif "multipart/form-data" in content_type:
        form = await request.form()
        folder_path = form.get("folder_path")
        prompt = form.get("prompt")
        for item in form.getlist("files"):
            if hasattr(item, "read"):
                files.append(item)
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Content-Type must be application/json or multipart/form-data"},
        )

    if not files and not folder_path:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide folder_path or upload files"},
        )

    run_id = str(uuid.uuid4())

    # Save uploaded files to a temp directory
    uploaded_paths: list[str] = []
    tmp_dir: str | None = None
    if files:
        tmp_dir = tempfile.mkdtemp(prefix="invoice_run_")
        for f in files:
            filename = getattr(f, "filename", None)
            if filename:
                dest = os.path.join(tmp_dir, filename)
                content = await f.read()
                if len(content) > MAX_UPLOAD_BYTES:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"File '{filename}' exceeds {settings.max_upload_size_mb}MB limit"},
                    )
                with open(dest, "wb") as out:
                    out.write(content)
                uploaded_paths.append(dest)

    return EventSourceResponse(
        _stream_run(run_id, folder_path, uploaded_paths, prompt, tmp_dir),
        media_type="text/event-stream",
    )


async def _stream_run(
    run_id: str,
    folder_path: str | None,
    uploaded_files: list[str],
    prompt: str | None,
    tmp_dir: str | None = None,
) -> AsyncGenerator[dict[str, str], None]:
    """Execute the LangGraph agent and yield SSE events."""
    tracer = RunTracer(run_id)
    tracer.start_run()

    try:
        # Emit run_started
        yield format_sse(run_started_event(run_id))

        llm_client = create_llm_client()
        compiled = compile_graph(llm_client)

        initial_state: dict[str, Any] = {
            "run_id": run_id,
            "folder_path": folder_path,
            "uploaded_files": uploaded_files,
            "prompt": prompt,
            "current_step": "load_images",
            "image_refs": [],
            "raw_extractions": [],
            "normalized_invoices": [],
            "categorized_invoices": [],
            "steps_completed": [],
            "issues": [],
        }

        # Node-to-step name mapping for SSE events
        node_step_names = {
            "load_images": "Loading invoice images",
            "extract": "Extracting invoice fields (Vision LLM)",
            "normalize": "Normalizing extracted data",
            "categorize": "Categorizing invoices (LLM)",
            "aggregate": "Aggregating totals",
            "report": "Generating final report",
        }

        prev_step = "start"
        running_state = dict(initial_state)
        async for event in compiled.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                if node_name == "planner":
                    continue

                # Log planner decision: what it routed from -> to
                planner_span = tracer.start_span(
                    "planner_decision",
                    {"from": prev_step, "routed_to": node_name},
                )
                tracer.end_span(planner_span, {"decision": f"{prev_step} -> {node_name}"})
                prev_step = node_name

                step_label = node_step_names.get(node_name, node_name)
                span = tracer.start_span(node_name, {"step": step_label})

                # tool_call event
                inputs_summary = _summarize_inputs(node_name, running_state)
                yield format_sse(tool_call_event(run_id, node_name, inputs_summary))

                # progress event
                yield format_sse(progress_event(run_id, node_name, step_label))

                # tool_result event
                outputs_summary = _summarize_outputs(node_name, node_output)
                yield format_sse(tool_result_event(run_id, node_name, outputs_summary))

                tracer.end_span(span, outputs_summary)
                running_state.update(node_output)

                # Emit invoice_result events for each newly categorized invoice
                new_categorized = node_output.get("categorized_invoices", [])
                for inv in new_categorized:
                    inv_data = inv.model_dump() if hasattr(inv, "model_dump") else inv
                    # Convert enums and nested models for JSON serialization
                    inv_json = json.loads(json.dumps(inv_data, default=str))
                    yield format_sse(invoice_result_event(run_id, inv_json))

                # Check if we have the final result
                final = node_output.get("final_result")
                if final is not None:
                    result_data = final.model_dump() if hasattr(final, "model_dump") else final
                    result_json = json.loads(json.dumps(result_data, default=str))
                    yield format_sse(final_result_event(run_id, result_json))

        tracer.end_run()
        # Save trace in background to avoid blocking the SSE stream
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, tracer.save_trace)

    except Exception as e:
        logger.exception("Run %s failed: %s", run_id, e)
        tracer.record_error(str(e))
        tracer.end_run()
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, tracer.save_trace)
        yield format_sse(error_event(run_id, str(e)))

    finally:
        # Clean up temp files from uploads
        if tmp_dir and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)
            logger.debug("Cleaned up temp dir: %s", tmp_dir)


def _summarize_inputs(node_name: str, state: dict[str, Any]) -> dict[str, Any]:
    """Create a brief summary of inputs for the SSE tool_call event."""
    if node_name == "load_images":
        return {"folder_path": state.get("folder_path"), "uploaded_count": len(state.get("uploaded_files", []))}
    if node_name == "extract":
        return {"image_count": len(state.get("image_refs", []))}
    if node_name == "normalize":
        return {"extraction_count": len(state.get("raw_extractions", []))}
    if node_name == "categorize":
        return {"invoice_count": len(state.get("normalized_invoices", []))}
    if node_name == "aggregate":
        return {"invoice_count": len(state.get("categorized_invoices", []))}
    if node_name == "report":
        return {"has_aggregation": state.get("aggregation") is not None}
    return {}


def _summarize_outputs(node_name: str, output: dict[str, Any]) -> dict[str, Any]:
    """Create a brief summary of outputs for the SSE tool_result event."""
    if node_name == "load_images":
        refs = output.get("image_refs", [])
        return {"images_loaded": len(refs)}
    if node_name == "extract":
        exts = output.get("raw_extractions", [])
        return {"invoices_extracted": len(exts)}
    if node_name == "normalize":
        norms = output.get("normalized_invoices", [])
        return {"invoices_normalized": len(norms)}
    if node_name == "categorize":
        cats = output.get("categorized_invoices", [])
        return {"invoices_categorized": len(cats)}
    if node_name == "aggregate":
        agg = output.get("aggregation")
        if agg and hasattr(agg, "total_spend"):
            return {"total_spend": agg.total_spend, "categories": len(agg.by_category)}
        return {}
    if node_name == "report":
        return {"final_result_generated": output.get("final_result") is not None}
    return {}
