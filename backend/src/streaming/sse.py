from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.models.events import SSEEvent, SSEEventType


def make_event(event_type: SSEEventType, run_id: str, data: dict[str, Any] | None = None) -> SSEEvent:
    return SSEEvent(
        event=event_type,
        run_id=run_id,
        data=data or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def format_sse(event: SSEEvent) -> dict[str, str]:
    """Format an SSEEvent for sse-starlette's EventSourceResponse."""
    return {
        "event": event.event.value,
        "data": json.dumps({
            "run_id": event.run_id,
            "timestamp": event.timestamp,
            **event.data,
        }),
    }


# Convenience helpers
def run_started_event(run_id: str, image_count: int = 0) -> SSEEvent:
    return make_event(SSEEventType.RUN_STARTED, run_id, {
        "message": "Invoice processing run started",
        "image_count": image_count,
    })


def progress_event(run_id: str, step: str, message: str, detail: Any = None) -> SSEEvent:
    data: dict[str, Any] = {"step": step, "message": message}
    if detail is not None:
        data["detail"] = detail
    return make_event(SSEEventType.PROGRESS, run_id, data)


def tool_call_event(run_id: str, tool_name: str, inputs_summary: dict[str, Any] | None = None) -> SSEEvent:
    return make_event(SSEEventType.TOOL_CALL, run_id, {
        "tool": tool_name,
        "inputs": inputs_summary or {},
    })


def tool_result_event(run_id: str, tool_name: str, outputs_summary: dict[str, Any] | None = None) -> SSEEvent:
    return make_event(SSEEventType.TOOL_RESULT, run_id, {
        "tool": tool_name,
        "outputs": outputs_summary or {},
    })


def invoice_result_event(run_id: str, invoice_data: dict[str, Any]) -> SSEEvent:
    return make_event(SSEEventType.INVOICE_RESULT, run_id, {"invoice": invoice_data})


def final_result_event(run_id: str, result_data: dict[str, Any]) -> SSEEvent:
    return make_event(SSEEventType.FINAL_RESULT, run_id, {"result": result_data})


def error_event(run_id: str, error_message: str, step: str | None = None) -> SSEEvent:
    data: dict[str, Any] = {"error": error_message}
    if step:
        data["step"] = step
    return make_event(SSEEventType.ERROR, run_id, data)
