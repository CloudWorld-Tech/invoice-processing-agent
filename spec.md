# API Specification

## Endpoints

### `GET /health`

Returns server status.

**Response:**
```json
{
  "status": "ok",
  "mock_mode": true,
  "model": "gpt-4o"
}
```

### `POST /runs/stream`

Start an invoice-processing run and stream SSE events.

**Request options:**

1. **JSON body** (folder path):
```json
{
  "folder_path": "sample_invoices",
  "prompt": "optional instruction for the agent"
}
```

2. **Multipart form** (file upload):
```
files: [binary image files]
folder_path: (optional) string
prompt: (optional) string
```

**Response:** `text/event-stream` (Server-Sent Events)

---

## SSE Event Schema

All events follow this structure:
```
event: <event_type>
data: {"run_id": "<uuid>", "timestamp": "<ISO-8601>", ...}
```

### `run_started`
```json
{
  "run_id": "uuid",
  "timestamp": "2024-12-10T...",
  "message": "Invoice processing run started",
  "image_count": 5
}
```

### `progress`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "step": "extract",
  "message": "Extracting invoice fields (Vision LLM)"
}
```

### `tool_call`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "tool": "load_images",
  "inputs": {"folder_path": "sample_invoices", "uploaded_count": 0}
}
```

### `tool_result`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "tool": "load_images",
  "outputs": {"images_loaded": 5}
}
```

### `invoice_result`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "invoice": {
    "vendor": "Delta Airlines",
    "invoice_date": "2024-11-15",
    "invoice_number": "DL-2024-78432",
    "total": 1250.00,
    "category": "Travel (air/hotel)",
    "confidence": 0.96,
    "notes": "Domestic flight booking",
    "line_items": ["Round-trip flight SFO-JFK", "Seat upgrade"],
    "image_ref": {"file_path": "...", "file_name": "...", "index": 0},
    "issues": []
  }
}
```

### `final_result`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "result": {
    "total_spend": 2500.05,
    "invoice_count": 5,
    "spend_by_category": [
      {"category": "Travel (air/hotel)", "total": 1739.50, "count": 2},
      {"category": "Meals & Entertainment", "total": 387.25, "count": 1},
      {"category": "Software / Subscriptions", "total": 231.00, "count": 1},
      {"category": "Office Supplies", "total": 142.30, "count": 1}
    ],
    "invoices": [ ... ],
    "issues_and_assumptions": [
      "No issues detected. All invoices processed successfully."
    ]
  }
}
```

### `error`
```json
{
  "run_id": "uuid",
  "timestamp": "...",
  "error": "Folder not found: /bad/path",
  "step": "load_images"
}
```

---

## Tool Registry

| # | Tool | Uses LLM | Description |
|---|---|---|---|
| 1 | `load_images` | No | Load invoice images from folder or uploaded files |
| 2 | `extract_invoice_fields` | Yes (Vision) | Extract structured fields from invoice image |
| 3 | `normalize_invoice` | No | Clean and normalize dates, amounts, vendor names |
| 4 | `categorize_invoice` | Yes | Assign expense category with confidence score |
| 5 | `aggregate` | No | Sum totals, group by category |
| 6 | `generate_report` | No | Build final structured output |

### Tool Schemas

#### `load_images`
- **Input:** `folder_path: str | None`, `uploaded_files: list[str] | None`
- **Output:** `list[ImageRef]` — `{file_path, file_name, index}`

#### `extract_invoice_fields`
- **Input:** `image_ref: ImageRef`, `llm_client`, `prompt: str | None`
- **Output:** `RawInvoiceFields` — `{vendor, invoice_date, invoice_number, total, line_items, raw_text, confidence}`

#### `normalize_invoice`
- **Input:** `raw: RawInvoiceFields`, `image_ref: ImageRef`
- **Output:** `NormalizedInvoice` — cleaned fields + issues list

#### `categorize_invoice`
- **Input:** `invoice: NormalizedInvoice`, `llm_client`, `prompt: str | None`
- **Output:** `CategorizedInvoice` — `{..., category, confidence, notes}`

#### `aggregate`
- **Input:** `invoices: list[CategorizedInvoice]`
- **Output:** `AggregationResult` — `{total_spend, by_category, invoice_count}`

#### `generate_report`
- **Input:** `aggregation`, `invoices`, `issues`
- **Output:** `FinalResult` — complete structured output

---

## Allowed Expense Categories

- Travel (air/hotel)
- Meals & Entertainment
- Software / Subscriptions
- Professional Services
- Office Supplies
- Shipping / Postage
- Utilities
- Other (must include explanatory note)

---

## Final Output Schema

```json
{
  "total_spend": 2500.05,
  "invoice_count": 5,
  "spend_by_category": [
    {"category": "Travel (air/hotel)", "total": 1739.50, "count": 2}
  ],
  "invoices": [
    {
      "vendor": "Delta Airlines",
      "invoice_date": "2024-11-15",
      "invoice_number": "DL-2024-78432",
      "total": 1250.00,
      "category": "Travel (air/hotel)",
      "confidence": 0.96,
      "notes": "Domestic flight booking",
      "line_items": ["Round-trip flight SFO-JFK", "Seat upgrade"],
      "issues": []
    }
  ],
  "issues_and_assumptions": [
    "No issues detected. All invoices processed successfully."
  ]
}
```
