"""Tests for the RunTracer."""
import json
import os

import pytest

from src.tracing.tracer import RunTracer, TraceSpan


class TestTraceSpan:
    def test_create(self):
        span = TraceSpan("s1", "test_step", {"key": "val"})
        assert span.span_id == "s1"
        assert span.name == "test_step"
        assert span.inputs == {"key": "val"}
        assert span.end_time is None

    def test_to_dict(self):
        span = TraceSpan("s1", "test")
        d = span.to_dict()
        assert d["span_id"] == "s1"
        assert d["duration_ms"] is None


class TestRunTracer:
    def test_start_and_end(self):
        tracer = RunTracer("run-1")
        tracer.start_run()
        assert tracer.start_time is not None
        tracer.end_run()
        assert tracer.end_time is not None

    def test_spans(self):
        tracer = RunTracer("run-1")
        span = tracer.start_span("step1", {"in": 1})
        tracer.end_span(span, {"out": 2})
        assert len(tracer.spans) == 1
        assert tracer.spans[0].outputs == {"out": 2}

    def test_record_error(self):
        tracer = RunTracer("run-1")
        tracer.record_error("something broke")
        assert tracer.error == "something broke"

    def test_save_trace(self, tmp_path):
        tracer = RunTracer("run-save", traces_dir=str(tmp_path))
        tracer.start_run()
        span = tracer.start_span("s1")
        tracer.end_span(span, {"ok": True})
        tracer.end_run()
        path = tracer.save_trace()

        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["run_id"] == "run-save"
        assert len(data["spans"]) == 1
        assert data["duration_ms"] is not None
        assert data["duration_ms"] >= 0

    def test_to_dict(self):
        tracer = RunTracer("run-dict")
        tracer.start_run()
        tracer.end_run()
        d = tracer.to_dict()
        assert d["run_id"] == "run-dict"
        assert d["span_count"] == 0
