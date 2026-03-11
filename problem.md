Software Development Manager – AI Platform
Architecture & AI Coding Challenge
Part 1: AI Coding Exercise
The Problem
Build (primarily using AI coding tools) a local invoice-processing agent exposed via an HTTP API that:
1.
Accepts a folder of images containing invoices
2.
Extracts relevant invoice information
3.
Summarizes costs by expense category
4.
Streams agent progress, trajectory, and final results via Server-Sent Events (SSE)
5.
Produces observable, reviewable execution traces
Use of AI Coding Tools (Required)
You are explicitly required to use any local AI coding tools you prefer, including:
•
GitHub Copilot
•
Claude Code
•
Cursor
•
ChatGPT
•
Other AI-assisted development tools
We want to see:
•
How you leverage AI productively
•
Where you apply judgment
•
How you validate or correct AI-generated code
•
Where AI should not be trusted in this workflow
This is not a test of manual coding speed. It is a test of system design, correctness, and
use of AI tools.
Timebox
2–3 hours total. Do not over-engineer.
Allowed Technology
• Preferred: Python + FastAPI or Node + Express
• You may use any LLM of choice, whether locally or cloud hosted
• Local execution only
• LocalStack (or comparable Docker runtime)
• You may use an industry-standard agent framework such as:
o LangChain
o Strands
o Claude Code
If you choose not to use a framework, briefly explain why in DESIGN.md.
OCR/VLM/LLM usage may be real or mocked (mock mode recommended).
Functional Requirements
Your agent must produce:
• Total spend across all invoices
• Spend by expense category
• Per-invoice structured output:
 Vendor
 Invoice date
 Invoice number (if present)
 Total
 Assigned category
 Confidence or notes
• A short “Issues & Assumptions” section
Example allowed categories
• Travel (air/hotel)
• Meals & Entertainment
• Software / Subscriptions
• Professional Services
• Office Supplies
• Shipping / Postage
• Utilities
• Other (must include explanatory note)
You may introduce internal subcategories, but final output must map to one of the above.
What to Build
1) HTTP Streaming Endpoint (Required)
POST /runs/stream
This endpoint must:
• Start a new invoice-processing run
• Immediately return an SSE stream
• Stream execution events until completion or failure
Request
• multipart/form-data with one or more invoice images and optional prompt, or
• JSON body with a local folder path and optional prompt
The optional prompt should influence agent behavior (e.g., conservative categorization,
flag unusual invoices, etc.).
Streaming Requirements
The server must stream:
• run_started
• progress
• tool_call
• tool_result
• invoice_result
• final_result
• error (if applicable)
The stream remains open until:
• All invoices are processed and final_result is emitted, or an unrecoverable error
occurs
2) Constrained Tool System & Guardrails (Required)
Your agent must operate through a clearly defined tool registry (4–6 tools).
The agent may only access invoice data via these tools.
Example tools (you may rename/adjust as you see fit):
1. load_images(input) -> [image_refs]
2. extract_invoice_fields(image_ref) -> structured_fields
3. normalize_invoice(fields) -> normalized_fields
4. categorize_invoice(normalized_fields, allowed_categories) -> {category,
confidence, notes}
5. aggregate(invoices) -> totals
6. generate_report(aggregates, invoices, issues) -> final_output
3) Required Output
The final structured output must include:
Run-Level Summary
• Total spend across all invoices
• Spend by expense category
• “Issues & Assumptions” section
Per-Invoice Structured Output
• Vendor
• Invoice date
• Invoice number (if present)
• Total
• Assigned category
• Confidence or notes
4) Tracing & Observability
Each run must produce a reviewable trace of execution.
You may implement this via:
• Structured logs (JSON recommended), and/or
• A third-party tracing tool (Langfuse, LangSmith, OpenTelemetry, etc.)
At minimum, the trace must capture:
• Step boundaries (extraction, normalization, categorization, aggregation, reporting)
• Tool calls and summarized inputs/outputs
• Planner decisions (high-level summaries)
• Errors or retries
• Timing information
The trace should allow a reviewer to understand:
• What the agent did
• In what order
• Why the final output was produced
Deliverables
Submit a single repository containing:
README.md with prerequisites, setup instructions, how to run the API, a curl example for
POST /runs/stream, example SSE output, and mock mode instructions (if implemented).
spec.md defining the /runs/stream contract, SSE event schema, tool registry and
schemas, and final output schema.
A /transcripts/ folder containing raw AI coding tool interaction logs.
Your source code implementing the streaming endpoint, tool registry, agent orchestration,
trajectory streaming, structured output, and tracing/observability.
DESIGN.md (max 1 page) summarizing your architecture, framework choice (if any),
planner/execution/state separation, model selection rationale, and what you would
improve for production.
Include at least one sample run trace showing execution steps and final output.
If applicable, include any agent configuration files (e.g., AGENTS.md, MCP setup, tool
authorization configuration) reflecting your AI-assisted development setup.