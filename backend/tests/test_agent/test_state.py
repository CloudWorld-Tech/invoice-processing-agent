"""Tests for agent state definition."""
from src.agent.state import AgentState, _append_list


class TestAppendList:
    def test_appends(self):
        assert _append_list([1, 2], [3, 4]) == [1, 2, 3, 4]

    def test_empty(self):
        assert _append_list([], [1]) == [1]

    def test_both_empty(self):
        assert _append_list([], []) == []


class TestAgentState:
    def test_state_is_typed_dict(self):
        # AgentState should accept the expected keys
        state: AgentState = {
            "run_id": "test",
            "current_step": "load_images",
        }
        assert state["run_id"] == "test"
