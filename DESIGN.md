# Design Document

## Architecture

```
React Dashboard (Vite)  ←SSE→  FastAPI Backend  →  LangGraph Agent  →  6-Tool Registry  →  LLM Client Layer
                                     ↕                    ↕                                        ↕
                                CORS + nginx          State (TypedDict)                    OpenAI / Mock
                                                          ↕
                                                   RunTracer (JSON)  +  LangSmith
```

The system is a **planner-executor agent** built on LangGraph. A planner node inspects the current state and routes to the appropriate tool node via conditional edges. After each tool executes, control returns to the planner, which decides the next step. This continues until all 6 pipeline stages complete. The React frontend connects via SSE to display real-time progress, per-invoice results, and final summary.

### System Flow Diagram

See [`diagrams/system-flow.mmd`](diagrams/system-flow.mmd) — high-level view of Frontend, Backend, Agent, LLM Client Layer, and Observability.

### Agent Detail Diagram

See [`diagrams/agent-detail.mmd`](diagrams/agent-detail.mmd) — planner-executor loop, 6 tool nodes, AgentState, SSE events, and tracing spans.

## Framework Choice: LangGraph

**Why LangGraph over a custom orchestrator:**
- Native state management with reducer functions (annotated lists auto-append)
- Built-in streaming (`astream`) maps directly to SSE event emission
- Conditional edges give us a true agent loop with planner decisions in traces
- LangSmith integration is automatic — every graph execution is traced
- Graph visualization helps explain architecture in walkthroughs

**Why not LangChain agents:** The invoice pipeline is more structured than a free-form ReAct agent. LangGraph's explicit graph definition gives us deterministic routing while still maintaining the planner-executor pattern.

## Planner / Execution / State Separation

| Layer | Responsibility | Location |
|---|---|---|
| **Planner** | Decides next step based on `current_step` in state | `backend/src/agent/nodes.py` → `planner_decide()` |
| **Execution** | Tool nodes that transform state | `backend/src/agent/nodes.py` → `*_node()` functions |
| **State** | TypedDict with annotated reducers | `backend/src/agent/state.py` → `AgentState` |
| **Streaming** | SSE event emission per node | `backend/src/main.py` → `_stream_run()` |
| **Frontend** | Real-time dashboard consuming SSE | `frontend/src/hooks/useInvoiceRun.ts` |

The planner is deterministic (sequential pipeline), but the architecture supports dynamic routing — e.g., retry failed extractions or skip already-processed invoices.

## Model Selection Rationale

- **GPT-4o** (via Azure OpenAI): Best vision capabilities for invoice image extraction. Configurable `base_url` and `api_key` support Azure deployments.
- Only 2 of 6 tools use the LLM (`extract_invoice_fields`, `categorize_invoice`). All others are pure Python.
- **Mock mode** replaces LLM calls with deterministic fixtures — same pipeline, zero cost.

## Tracing & Observability

Two complementary approaches:
1. **LangSmith**: Automatic tracing of all LangGraph executions. Zero-config when `LANGCHAIN_TRACING_V2=true`.
2. **Local JSON traces**: `RunTracer` writes per-run trace files to `backend/traces/` with planner decisions, span boundaries, timing, inputs/outputs, and errors.

## What I Would Improve for Production

1. **Graph-level retry**: The LLM client retries individual API calls, but graph-level retry (re-running a failed node with backoff and circuit breaker) would improve resilience for transient failures mid-pipeline.
2. **Persistent state**: Use LangGraph checkpointing (Redis/Postgres) for run recovery after crashes.
3. **Authentication**: Add API key auth or OAuth2 to the FastAPI endpoints.
4. **Rate limiting**: Protect against abuse and OpenAI rate limits.
5. **Batch processing**: Support very large invoice folders with pagination and progress tracking.
6. **Confidence thresholds**: Auto-flag low-confidence extractions for human review queue.
7. **Caching**: Cache LLM responses for identical images (content-hash keyed) to reduce cost.
8. **Structured output**: Use OpenAI's structured output mode (function calling) instead of JSON mode for more reliable extraction.
9. **Missing field detection**: Detect and flag missing invoice numbers during normalization for reviewer attention.
10. **Monitoring**: Add Prometheus metrics for latency, error rates, and LLM token usage.
