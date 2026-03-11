// --- Discriminated SSE event types ---

export interface RunStartedEvent {
  event: "run_started";
  data: { run_id: string; message: string; image_count?: number };
}

export interface ProgressEvent {
  event: "progress";
  data: { step: string; message: string; detail?: unknown };
}

export interface ToolCallEvent {
  event: "tool_call";
  data: { tool: string; inputs: Record<string, unknown> };
}

export interface ToolResultEvent {
  event: "tool_result";
  data: { tool: string; outputs: Record<string, unknown> };
}

export interface InvoiceResultEvent {
  event: "invoice_result";
  data: { invoice: InvoiceResult };
}

export interface FinalResultEvent {
  event: "final_result";
  data: { result: FinalResult };
}

export interface ErrorEvent {
  event: "error";
  data: { error: string; step?: string };
}

export type SSEEvent =
  | RunStartedEvent
  | ProgressEvent
  | ToolCallEvent
  | ToolResultEvent
  | InvoiceResultEvent
  | FinalResultEvent
  | ErrorEvent;

export type SSEEventType = SSEEvent["event"];

// --- Domain types ---

export interface InvoiceResult {
  vendor: string;
  invoice_date: string;
  invoice_number: string | null;
  total: number;
  category: string;
  confidence: number;
  line_items: string[];
  issues: string[];
  flags: string[];
}

export interface CategorySpend {
  category: string;
  total: number;
  count: number;
}

export interface FinalResult {
  invoice_count: number;
  total_spend: number;
  spend_by_category: CategorySpend[];
  invoices: InvoiceResult[];
  issues_and_assumptions: string[];
  flags: string[];
}

export interface ProgressStep {
  node: string;
  label: string;
  status: "pending" | "running" | "completed" | "error";
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
}

export type RunStatus = "idle" | "connecting" | "running" | "completed" | "error";

export type SortField = "vendor" | "invoice_date" | "total" | "category" | "confidence";
export type SortDirection = "asc" | "desc";
