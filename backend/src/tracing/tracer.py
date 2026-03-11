from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any


class TraceSpan:
    def __init__(self, span_id: str, name: str, inputs: dict[str, Any] | None = None):
        self.span_id = span_id
        self.name = name
        self.inputs = inputs or {}
        self.outputs: dict[str, Any] = {}
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.end_time: str | None = None
        self.error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
            "duration_ms": self._duration_ms(),
        }

    def _duration_ms(self) -> float | None:
        if not self.end_time:
            return None
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds() * 1000


class RunTracer:
    """Local trace recorder that writes JSONL trace files to /traces/."""

    def __init__(self, run_id: str, traces_dir: str = "traces"):
        self.run_id = run_id
        self.traces_dir = traces_dir
        self.spans: list[TraceSpan] = []
        self.start_time: str | None = None
        self.end_time: str | None = None
        self.error: str | None = None

    def start_run(self) -> None:
        self.start_time = datetime.now(timezone.utc).isoformat()

    def end_run(self) -> None:
        self.end_time = datetime.now(timezone.utc).isoformat()

    def start_span(self, name: str, inputs: dict[str, Any] | None = None) -> TraceSpan:
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            name=name,
            inputs=inputs,
        )
        self.spans.append(span)
        return span

    def end_span(self, span: TraceSpan, outputs: dict[str, Any] | None = None) -> None:
        span.end_time = datetime.now(timezone.utc).isoformat()
        if outputs is not None:
            span.outputs = outputs

    def record_error(self, error: str, span: TraceSpan | None = None) -> None:
        self.error = error
        if span:
            span.error = error
            if not span.end_time:
                span.end_time = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        duration_ms = None
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            duration_ms = (end - start).total_seconds() * 1000

        return {
            "run_id": self.run_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": duration_ms,
            "span_count": len(self.spans),
            "error": self.error,
            "spans": [s.to_dict() for s in self.spans],
        }

    def save_trace(self) -> str:
        os.makedirs(self.traces_dir, exist_ok=True)
        path = os.path.join(self.traces_dir, f"{self.run_id}.json")
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return path
