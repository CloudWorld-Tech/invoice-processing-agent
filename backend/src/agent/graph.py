from __future__ import annotations

from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph

from src.agent.nodes import (
    aggregate_node,
    categorize_node,
    extract_node,
    load_images_node,
    normalize_node,
    planner_decide,
    report_node,
)
from src.agent.state import AgentState
from src.llm.base import BaseLLMClient


def build_graph(llm_client: BaseLLMClient) -> StateGraph:
    """Build the LangGraph invoice processing graph.

    Architecture:
        planner -> [load_images | extract | normalize | categorize | aggregate | report | END]
        Each tool node routes back to planner, which decides the next step.
    """
    graph = StateGraph(AgentState)

    # Bind the LLM client to each node via partial
    graph.add_node("load_images", partial(load_images_node, llm_client=llm_client))
    graph.add_node("extract", partial(extract_node, llm_client=llm_client))
    graph.add_node("normalize", partial(normalize_node, llm_client=llm_client))
    graph.add_node("categorize", partial(categorize_node, llm_client=llm_client))
    graph.add_node("aggregate", partial(aggregate_node, llm_client=llm_client))
    graph.add_node("report", partial(report_node, llm_client=llm_client))

    # Planner: conditional entry point that routes to the right tool
    graph.add_node("planner", _planner_node)

    # Entry
    graph.set_entry_point("planner")

    # Planner conditionally routes to a tool or END
    graph.add_conditional_edges(
        "planner",
        _route_from_planner,
        {
            "load_images": "load_images",
            "extract": "extract",
            "normalize": "normalize",
            "categorize": "categorize",
            "aggregate": "aggregate",
            "report": "report",
            "done": END,
        },
    )

    # Each tool routes back to planner
    for node_name in ["load_images", "extract", "normalize", "categorize", "aggregate", "report"]:
        graph.add_edge(node_name, "planner")

    return graph


def _planner_node(state: dict[str, Any]) -> dict[str, Any]:
    """Planner node — no state mutation, just passes through.
    The routing logic is in _route_from_planner."""
    return {}


def _route_from_planner(state: dict[str, Any]) -> str:
    """Decide which node to go to next based on the current step."""
    return planner_decide(state)


def compile_graph(llm_client: BaseLLMClient):
    """Build and compile the graph, returning a runnable."""
    graph = build_graph(llm_client)
    return graph.compile()
