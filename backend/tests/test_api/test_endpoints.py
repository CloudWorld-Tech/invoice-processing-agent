"""Tests for FastAPI endpoints."""
import json
import os

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def sample_invoices_dir():
    """Return path to the sample_invoices directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "sample_invoices")
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        return abs_path
    return None


class TestHealth:
    @pytest.mark.asyncio
    async def test_health(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["mock_mode"] is True


class TestRunsStream:
    @pytest.mark.asyncio
    async def test_missing_input_returns_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/runs/stream", json={})
            assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_json_body_with_folder(self, sample_invoices_dir):
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={"folder_path": sample_invoices_dir},
                timeout=30.0,
            )
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")

            # Parse SSE events from response
            events = _parse_sse_events(resp.text)
            event_types = [e["event"] for e in events]

            assert "run_started" in event_types
            assert "tool_call" in event_types
            assert "tool_result" in event_types
            assert "final_result" in event_types

    @pytest.mark.asyncio
    async def test_json_body_with_prompt(self, sample_invoices_dir):
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={
                    "folder_path": sample_invoices_dir,
                    "prompt": "flag anything over $500",
                },
                timeout=30.0,
            )
            assert resp.status_code == 200
            events = _parse_sse_events(resp.text)
            assert any(e["event"] == "final_result" for e in events)

    @pytest.mark.asyncio
    async def test_sse_event_order(self, sample_invoices_dir):
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={"folder_path": sample_invoices_dir},
                timeout=30.0,
            )
            events = _parse_sse_events(resp.text)
            event_types = [e["event"] for e in events]

            # run_started should be first
            assert event_types[0] == "run_started"
            # final_result should be last
            assert event_types[-1] == "final_result"

    @pytest.mark.asyncio
    async def test_final_result_structure(self, sample_invoices_dir):
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={"folder_path": sample_invoices_dir},
                timeout=30.0,
            )
            events = _parse_sse_events(resp.text)
            final_events = [e for e in events if e["event"] == "final_result"]
            assert len(final_events) == 1

            final_data = final_events[0]["data"]
            result = final_data["result"]
            assert "total_spend" in result
            assert "spend_by_category" in result
            assert "invoices" in result
            assert "issues_and_assumptions" in result
            assert result["invoice_count"] == 5

    @pytest.mark.asyncio
    async def test_invoice_result_events(self, sample_invoices_dir):
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={"folder_path": sample_invoices_dir},
                timeout=30.0,
            )
            events = _parse_sse_events(resp.text)
            invoice_events = [e for e in events if e["event"] == "invoice_result"]
            assert len(invoice_events) == 5

            for ie in invoice_events:
                inv = ie["data"]["invoice"]
                assert "vendor" in inv
                assert "total" in inv
                assert "category" in inv

    @pytest.mark.asyncio
    async def test_nonexistent_folder(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                json={"folder_path": "/nonexistent/path"},
                timeout=30.0,
            )
            assert resp.status_code == 200  # SSE stream starts, error comes as event
            events = _parse_sse_events(resp.text)
            event_types = [e["event"] for e in events]
            assert "error" in event_types

    @pytest.mark.asyncio
    async def test_invalid_json_returns_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                content=b"not json at all",
                headers={"Content-Type": "application/json"},
            )
            assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_multipart_with_files(self, sample_invoices_dir):
        """Test multipart/form-data upload with invoice files."""
        if not sample_invoices_dir:
            pytest.skip("sample_invoices not found")

        # Get the first image file from sample_invoices
        image_files = sorted(
            f for f in os.listdir(sample_invoices_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp"))
        )
        if not image_files:
            pytest.skip("No image files in sample_invoices")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Upload the first 2 images (or 1 if only 1 exists)
            files_to_upload = image_files[:2]
            upload_files = []
            for fname in files_to_upload:
                fpath = os.path.join(sample_invoices_dir, fname)
                upload_files.append(("files", (fname, open(fpath, "rb"), "image/png")))

            resp = await client.post(
                "/runs/stream",
                files=upload_files,
                timeout=30.0,
            )

            # Close file handles
            for _, (_, fh, _) in upload_files:
                fh.close()

            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")

            events = _parse_sse_events(resp.text)
            event_types = [e["event"] for e in events]
            assert "run_started" in event_types
            assert "final_result" in event_types

    @pytest.mark.asyncio
    async def test_multipart_no_files_or_folder_returns_400(self):
        """Multipart request with neither files nor folder_path should fail."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/runs/stream",
                data={"prompt": "test"},
                timeout=10.0,
            )
            assert resp.status_code == 400


def _parse_sse_events(text: str) -> list[dict]:
    """Parse SSE text format into list of dicts with event and data."""
    events = []
    current_event = None
    current_data = ""

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("event:"):
            current_event = line[len("event:"):].strip()
        elif line.startswith("data:"):
            current_data = line[len("data:"):].strip()
        elif line == "" and current_event:
            try:
                data = json.loads(current_data) if current_data else {}
            except json.JSONDecodeError:
                data = {"raw": current_data}
            events.append({"event": current_event, "data": data})
            current_event = None
            current_data = ""

    # Handle last event if no trailing newline
    if current_event:
        try:
            data = json.loads(current_data) if current_data else {}
        except json.JSONDecodeError:
            data = {"raw": current_data}
        events.append({"event": current_event, "data": data})

    return events
