# Invoice Processing Agent

Local invoice-processing agent exposed via HTTP API with Server-Sent Events (SSE) streaming, LangGraph orchestration, LangSmith tracing, and a React dashboard.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Option A: Run Locally](#option-a-run-locally)
- [Option B: Run with Docker](#option-b-run-with-docker)
- [Configuration Reference](#configuration-reference)
- [Mock Mode vs Real Mode](#mock-mode-vs-real-mode)
- [API Usage](#api-usage)
- [Running Tests](#running-tests)

---

## Prerequisites

### For local development

| Tool | Version | How to install |
|---|---|---|
| **Python** | 3.12+ | [python.org/downloads](https://www.python.org/downloads/) |
| **uv** | latest | `pip install uv` or see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org/) (includes npm) |

### For Docker (alternative)

| Tool | Version | How to install |
|---|---|---|
| **Docker** | 20+ | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2+ | Included with Docker Desktop |

> **No API keys are required** to run in mock mode (the default). You only need an OpenAI or Azure OpenAI key if you want to process real invoices with a vision LLM.

---

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app + /runs/stream endpoint + CORS
│   │   ├── config.py            # pydantic-settings configuration
│   │   ├── models/              # Pydantic data models
│   │   ├── agent/               # LangGraph graph, planner, nodes, state
│   │   ├── tools/               # 6-tool registry + implementations
│   │   ├── llm/                 # LLM client abstraction (OpenAI + Mock)
│   │   ├── streaming/           # SSE event formatting
│   │   └── tracing/             # Local JSON trace recorder
│   ├── tests/                   # 93 tests
│   ├── scripts/                 # Invoice generation script
│   ├── sample_invoices/         # 5 synthetic PNG invoices
│   ├── traces/                  # Run trace output (JSON)
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/                     # React + TypeScript UI
│   │   ├── components/          # Header, InputPanel, PipelineProgress, InvoiceTable, SummaryPanel, EventLog
│   │   ├── hooks/               # useInvoiceRun (SSE streaming hook)
│   │   ├── types/               # TypeScript types
│   │   └── api/                 # API config
│   ├── Dockerfile               # Multi-stage (node build → nginx)
│   └── nginx.conf               # SPA routing + /api proxy
├── docker-compose.yml           # backend:8000 + frontend:3000
├── transcripts/                 # AI coding tool interaction logs
├── spec.md                      # API contract specification
├── DESIGN.md                    # Architecture & design decisions
└── CLAUDE.md                    # AI-assisted development configuration
```

---

## Option A: Run Locally

### Step 1: Install backend dependencies

```bash
cd backend
uv sync --extra dev
```

This creates a `.venv` virtual environment and installs all Python packages (FastAPI, LangGraph, langchain-openai, etc.).

### Step 2: Generate sample invoices

The project includes a script that creates 5 synthetic PNG invoice images:

```bash
cd backend
uv run python scripts/generate_sample_invoices.py
```

This creates `backend/sample_invoices/` with 5 invoice PNG files. These are used by both mock and real modes.

### Step 3: Configure the backend

```bash
cd backend
cp .env.example .env
```

Open `backend/.env` in a text editor. For **mock mode** (no API keys needed), the defaults work as-is:

```env
MOCK_MODE=true
```

For **real mode** (uses a vision LLM to extract invoice data), see [Mock Mode vs Real Mode](#mock-mode-vs-real-mode) below.

### Step 4: Start the backend

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

The API is now available at **http://localhost:8000**. Verify with:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok", "mock_mode": true, "model": "gpt-4o"}
```

### Step 5: Start the frontend

Open a **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

The dashboard is now available at **http://localhost:3000**.

### Step 6: Use the application

1. Open **http://localhost:3000** in your browser
2. Enter a folder path (e.g., `sample_invoices`) or upload invoice image files
3. Optionally add a prompt (e.g., "flag any invoice over $500")
4. Click **Process Invoices**
5. Watch the 6-step pipeline execute in real time via SSE streaming

---

## Option B: Run with Docker

### Step 1: Generate sample invoices

If you haven't already, generate the sample invoice images (requires Python + uv):

```bash
cd backend
uv sync
uv run python scripts/generate_sample_invoices.py
```

> If you don't have Python/uv installed locally, you can skip this — but the `sample_invoices/` folder must contain PNG files for the agent to process.

### Step 2: Configure the backend

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` as needed. For mock mode, the defaults work as-is.

### Step 3: Build and start both services

```bash
docker compose up --build
```

This builds and starts:
- **Backend** on **http://localhost:8000** (FastAPI + uvicorn)
- **Frontend** on **http://localhost:3000** (React app served by nginx, proxies `/api/*` to the backend)

### Step 4: Use the application

Open **http://localhost:3000** in your browser and process invoices as described above.

### Stopping the services

```bash
docker compose down
```

---

## Configuration Reference

All configuration is managed via `backend/.env`. Here is every available setting:

| Variable | Default | Required | Description |
|---|---|---|---|
| `MOCK_MODE` | `true` | No | When `true`, uses deterministic fixture data instead of calling an LLM. No API keys needed. |
| `OPENAI_API_KEY` | — | Only in real mode | Your OpenAI or Azure OpenAI API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | No | API base URL. Set to your Azure endpoint for Azure OpenAI. |
| `OPENAI_MODEL` | `gpt-4o` | No | Vision-capable model name (must support image inputs) |
| `AZURE_API_VERSION` | `2024-12-01-preview` | Only for Azure | Azure OpenAI API version. Auto-used when URL contains "azure". |
| `LANGCHAIN_TRACING_V2` | `false` | No | Set to `true` to enable LangSmith cloud tracing |
| `LANGCHAIN_API_KEY` | — | Only if tracing enabled | Your LangSmith API key (get one at [smith.langchain.com](https://smith.langchain.com)) |
| `LANGCHAIN_PROJECT` | `invoice-agent` | No | LangSmith project name for organizing traces |

---

## Mock Mode vs Real Mode

### Mock mode (`MOCK_MODE=true`) — Default

- **No API keys required**
- Uses deterministic fixture data for the 2 LLM-powered steps (extract + categorize)
- All other steps (load_images, normalize, aggregate, report) run real code
- SSE streaming, tracing, and output format work identically to real mode
- Produces the same JSON structure, just with fixed sample data

**When to use:** Local development, testing, demos, or when you don't have an API key.

`.env` for mock mode:

```env
MOCK_MODE=true
```

### Real mode (`MOCK_MODE=false`)

- **Requires an OpenAI or Azure OpenAI API key**
- Uses GPT-4o (or configured model) with vision capabilities to read invoice images
- Extracts real vendor names, dates, amounts, line items from the images
- Categorizes invoices using LLM reasoning

**When to use:** Processing actual invoice images with real LLM extraction.

`.env` for real mode with **standard OpenAI**:

```env
MOCK_MODE=false
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

`.env` for real mode with **Azure OpenAI**:

```env
MOCK_MODE=false
OPENAI_API_KEY=your-azure-api-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com
OPENAI_MODEL=gpt-4o
AZURE_API_VERSION=2024-12-01-preview
```

> Azure OpenAI is auto-detected when `OPENAI_BASE_URL` contains "azure". The client automatically switches to `AsyncAzureOpenAI`.

---

## API Usage

### Health check

```bash
curl http://localhost:8000/health
```

### Process invoices (folder path)

```bash
curl -N -X POST http://localhost:8000/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "sample_invoices"}'
```

### Process invoices with a prompt

```bash
curl -N -X POST http://localhost:8000/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "sample_invoices", "prompt": "flag any invoice over $500"}'
```

### Upload files (multipart)

```bash
curl -N -X POST http://localhost:8000/runs/stream \
  -F "files=@backend/sample_invoices/invoice_001_delta_airlines.png" \
  -F "files=@backend/sample_invoices/invoice_002_marriott.png"
```

### Example SSE Output

The stream emits events in this order: `run_started` → (`tool_call` → `progress` → `tool_result`) × 6 stages → `invoice_result` × N → `final_result`.

```
event: run_started
data: {"run_id":"a1b2c3d4-5678-90ab-cdef-111111111111","timestamp":"2026-03-10T04:09:50Z","message":"Invoice processing run started","image_count":5}

event: tool_call
data: {"run_id":"a1b2c3d4-...","timestamp":"...","tool":"load_images","inputs":{"folder_path":"sample_invoices","uploaded_count":0}}

event: progress
data: {"run_id":"a1b2c3d4-...","timestamp":"...","step":"load_images","message":"Loading invoice images"}

event: tool_result
data: {"run_id":"a1b2c3d4-...","timestamp":"...","tool":"load_images","outputs":{"images_loaded":5}}

event: tool_call
data: {"run_id":"a1b2c3d4-...","timestamp":"...","tool":"extract_invoice_fields","inputs":{"image_count":5}}

event: progress
data: {"run_id":"a1b2c3d4-...","timestamp":"...","step":"extract","message":"Extracting invoice fields (Vision LLM)"}

event: tool_result
data: {"run_id":"a1b2c3d4-...","timestamp":"...","tool":"extract_invoice_fields","outputs":{"invoices_extracted":5}}

... (normalize, categorize, aggregate, report stages follow the same pattern) ...

event: invoice_result
data: {"run_id":"a1b2c3d4-...","timestamp":"...","invoice":{"vendor":"Delta Airlines","invoice_date":"2024-11-15","invoice_number":"DL-2024-78432","total":1250.00,"category":"Travel (air/hotel)","confidence":0.96,"notes":"Domestic flight booking","line_items":["Round-trip flight SFO-JFK","Seat upgrade"],"issues":[]}}

event: final_result
data: {"run_id":"a1b2c3d4-...","timestamp":"...","result":{"total_spend":2500.05,"invoice_count":5,"spend_by_category":[{"category":"Travel (air/hotel)","total":1739.50,"count":2},{"category":"Meals & Entertainment","total":387.25,"count":1},{"category":"Software / Subscriptions","total":231.00,"count":1},{"category":"Office Supplies","total":142.30,"count":1}],"invoices":[...],"issues_and_assumptions":["No issues detected. All invoices processed successfully."]}}
```

On error, an `error` event is emitted:

```
event: error
data: {"run_id":"a1b2c3d4-...","timestamp":"...","error":"Folder not found: /bad/path","step":"load_images"}
```

---

## Running Tests

```bash
cd backend
uv run python -m pytest tests/ -v
```

93 tests covering models, tools, agent graph, API endpoints, and mock mode.

---

## Observability & Tracing

Every run produces a JSON trace file in `backend/traces/` with span-level timing, inputs, outputs, and planner decisions.

- **Local traces**: Automatic — see `backend/traces/` for JSON files after each run.
- **Sample trace**: `backend/traces/sample-run-001.json` contains a complete end-to-end trace showing all 6 pipeline stages with planner decisions and final output.
- **LangSmith**: Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` for cloud tracing of all LangGraph executions.
