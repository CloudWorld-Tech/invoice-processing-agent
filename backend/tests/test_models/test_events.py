"""Tests for SSE event models."""
from src.models.events import SSEEvent, SSEEventType


class TestSSEEventType:
    def test_all_event_types(self):
        expected = ["run_started", "progress", "tool_call", "tool_result", "invoice_result", "final_result", "error"]
        values = [e.value for e in SSEEventType]
        for exp in expected:
            assert exp in values

    def test_event_count(self):
        assert len(SSEEventType) == 7


class TestSSEEvent:
    def test_create(self):
        event = SSEEvent(
            event=SSEEventType.RUN_STARTED,
            run_id="test-123",
            data={"message": "started"},
        )
        assert event.event == SSEEventType.RUN_STARTED
        assert event.run_id == "test-123"

    def test_default_data(self):
        event = SSEEvent(event=SSEEventType.PROGRESS, run_id="r1")
        assert event.data == {}
        assert event.timestamp is None
