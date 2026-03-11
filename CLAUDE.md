# CLAUDE.md — AI-Assisted Development Configuration

This file documents the AI-assisted development setup used to build this project and provides context for future Claude Code sessions operating in this repository.

## Project Overview

Local invoice-processing agent with SSE streaming. A take-home coding challenge implementing a planner-executor agent that extracts, normalizes, categorizes, and aggregates expense invoices from images.

## Commands

### Backend
```bash
cd backend && uv sync --extra dev          # Install dependencies
cd backend && uv run uvicorn src.main:app --reload --port 8000  # Run API
cd backend && uv run python -m pytest tests/ -v                 # Run tests (93 tests)
```

### Frontend
```bash
cd frontend && npm install    # Install dependencies
cd frontend && npm run dev    # Dev server (Vite)
cd frontend && npm run build  # Production build
```

### Docker
```bash
docker compose up --build     # Backend:8000 + Frontend:3000
docker compose down           # Stop services
```

## Architecture

**Stack**: Python 3.12 + FastAPI + LangGraph + langchain-openai | React 19 + TypeScript + Vite

**Agent pipeline** (LangGraph planner-executor):
```
planner → load_images → planner → extract → planner → normalize → planner → categorize → planner → aggregate → planner → report → END
```

Each tool node writes to `AgentState` (TypedDict with annotated reducers), and the planner reads `current_step` to route via conditional edges.

**Key directories:**
- `backend/src/agent/` — LangGraph graph, planner, node functions, state
- `backend/src/tools/` — ToolRegistry + 6 tool modules
- `backend/src/llm/` — LLM abstraction (BaseLLMClient ABC → OpenAIClient, MockLLMClient)
- `backend/src/models/` — Pydantic v2 models (invoice, events, requests)
- `backend/src/streaming/` — SSE event formatting helpers
- `backend/src/tracing/` — RunTracer for local JSON trace files
- `frontend/src/hooks/` — useInvoiceRun SSE streaming hook
- `frontend/src/components/` — Dashboard UI components

## Environment Variables

Configured in `backend/.env` (see `backend/.env.example`):
- `MOCK_MODE=true` — Default. Deterministic fixtures, no API key needed.
- `OPENAI_API_KEY` — Required when MOCK_MODE=false
- `OPENAI_BASE_URL` — Azure auto-detected when URL contains "azure"
- `LANGCHAIN_TRACING_V2=true` — Enables LangSmith cloud tracing

## AI-Assisted Development Tool

- **Tool**: Claude Code (Anthropic CLI)
- **Model**: Claude Opus / Claude Sonnet
- **Session transcripts**: Stored in `transcripts/` (6 JSONL session files)
- **Usage**: Architecture design, code generation, testing, debugging, documentation
- **MCP servers**: None configured (standard tool access only)
- **Tool authorization**: Default Claude Code permissions (file read/write, bash, glob, grep)
