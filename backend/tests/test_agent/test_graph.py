"""Tests for the LangGraph agent graph."""
import pytest

from src.agent.graph import build_graph, compile_graph
from src.agent.nodes import STEP_ORDER, planner_decide
from src.llm.mock_client import MockLLMClient


class TestPlannerDecide:
    def test_initial_step(self):
        state = {}
        assert planner_decide(state) == "load_images"

    def test_each_step(self):
        for step in STEP_ORDER:
            assert planner_decide({"current_step": step}) == step

    def test_unknown_step_defaults(self):
        assert planner_decide({"current_step": "unknown"}) == "load_images"


class TestBuildGraph:
    def test_builds_without_error(self):
        client = MockLLMClient()
        graph = build_graph(client)
        assert graph is not None

    def test_compiles_without_error(self):
        client = MockLLMClient()
        compiled = compile_graph(client)
        assert compiled is not None


class TestGraphExecution:
    @pytest.mark.asyncio
    async def test_full_pipeline_mock(self, tmp_path):
        """Run the full graph with mock client and sample images."""
        # Create sample image files
        for i in range(3):
            (tmp_path / f"inv_{i}.png").write_bytes(b"\x89PNG")

        client = MockLLMClient()
        compiled = compile_graph(client)

        initial_state = {
            "run_id": "test-run-1",
            "folder_path": str(tmp_path),
            "uploaded_files": [],
            "prompt": None,
            "current_step": "load_images",
            "image_refs": [],
            "raw_extractions": [],
            "normalized_invoices": [],
            "categorized_invoices": [],
            "steps_completed": [],
            "issues": [],
        }

        # Collect all state updates
        updates = []
        async for event in compiled.astream(initial_state, stream_mode="updates"):
            updates.append(event)

        # Should have planner + tool node updates
        assert len(updates) > 0

        # Get final state
        final_state = await compiled.ainvoke(initial_state)
        assert final_state["final_result"] is not None
        assert final_state["final_result"].total_spend > 0
        assert final_state["final_result"].invoice_count == 3

    @pytest.mark.asyncio
    async def test_pipeline_with_prompt(self, tmp_path):
        """Test that prompt parameter flows through the pipeline."""
        (tmp_path / "test.png").write_bytes(b"\x89PNG")

        client = MockLLMClient()
        compiled = compile_graph(client)

        state = {
            "run_id": "test-prompt",
            "folder_path": str(tmp_path),
            "uploaded_files": [],
            "prompt": "flag unusual invoices",
            "current_step": "load_images",
            "image_refs": [],
            "raw_extractions": [],
            "normalized_invoices": [],
            "categorized_invoices": [],
            "steps_completed": [],
            "issues": [],
        }

        result = await compiled.ainvoke(state)
        assert result["final_result"] is not None
