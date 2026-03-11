import { useCallback, useRef, useState } from "react";
import { API_BASE_URL } from "../api/config";
import type {
  FinalResult,
  InvoiceResult,
  ProgressStep,
  RunStatus,
  SSEEvent,
} from "../types";

const MAX_EVENTS = 500;

const PIPELINE_STEPS = [
  { node: "load_images", label: "Loading invoice images" },
  { node: "extract", label: "Extracting invoice fields (Vision LLM)" },
  { node: "normalize", label: "Normalizing extracted data" },
  { node: "categorize", label: "Categorizing invoices (LLM)" },
  { node: "aggregate", label: "Aggregating totals" },
  { node: "report", label: "Generating final report" },
];

function initialSteps(): ProgressStep[] {
  return PIPELINE_STEPS.map((s) => ({ ...s, status: "pending" as const }));
}

export function useInvoiceRun() {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [runId, setRunId] = useState<string | null>(null);
  const [steps, setSteps] = useState<ProgressStep[]>(initialSteps());
  const [invoices, setInvoices] = useState<InvoiceResult[]>([]);
  const [finalResult, setFinalResult] = useState<FinalResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setStatus("idle");
    setRunId(null);
    setSteps(initialSteps());
    setInvoices([]);
    setFinalResult(null);
    setError(null);
    setEvents([]);
    setUploadProgress(null);
  }, []);

  const appendEvent = useCallback((evt: SSEEvent) => {
    setEvents((prev) => {
      const next = [...prev, evt];
      return next.length > MAX_EVENTS ? next.slice(-MAX_EVENTS) : next;
    });
  }, []);

  const startRunWithFolder = useCallback(
    async (folderPath: string, prompt?: string) => {
      reset();
      setStatus("connecting");

      const abort = new AbortController();
      abortRef.current = abort;

      try {
        const body: Record<string, string> = { folder_path: folderPath };
        if (prompt) body.prompt = prompt;

        const resp = await fetch(`${API_BASE_URL}/runs/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: abort.signal,
        });

        if (!resp.ok) {
          const err = await resp.json().catch(() => ({ error: resp.statusText }));
          throw new Error(err.error || `HTTP ${resp.status}`);
        }

        processSSEStream(resp);
      } catch (e: unknown) {
        if ((e as Error).name === "AbortError") return;
        setStatus("error");
        setError((e as Error).message);
      }
    },
    [reset]
  );

  const startRunWithFiles = useCallback(
    async (files: File[], prompt?: string) => {
      reset();
      setStatus("connecting");
      setUploadProgress(0);

      const abort = new AbortController();
      abortRef.current = abort;

      try {
        const formData = new FormData();
        files.forEach((f) => formData.append("files", f));
        if (prompt) formData.append("prompt", prompt);

        // Use XMLHttpRequest for upload progress tracking
        const resp = await new Promise<Response>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open("POST", `${API_BASE_URL}/runs/stream`);

          xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
              setUploadProgress(Math.round((e.loaded / e.total) * 100));
            }
          });

          xhr.addEventListener("load", () => {
            setUploadProgress(null);
            // Convert XHR response back to a fetch-like Response for SSE processing
            const headers = new Headers();
            xhr.getAllResponseHeaders().trim().split(/\r?\n/).forEach((line) => {
              const idx = line.indexOf(": ");
              if (idx > 0) headers.append(line.slice(0, idx), line.slice(idx + 2));
            });
            resolve(new Response(xhr.response, { status: xhr.status, headers }));
          });

          xhr.addEventListener("error", () => {
            setUploadProgress(null);
            reject(new Error("Network error during upload"));
          });

          xhr.addEventListener("abort", () => {
            setUploadProgress(null);
          });

          abort.signal.addEventListener("abort", () => xhr.abort());
          xhr.responseType = "blob";
          xhr.send(formData);
        });

        if (!resp.ok) {
          const text = await resp.text();
          let errMsg: string;
          try {
            errMsg = JSON.parse(text).error || `HTTP ${resp.status}`;
          } catch {
            errMsg = resp.statusText || `HTTP ${resp.status}`;
          }
          throw new Error(errMsg);
        }

        // For SSE we need a streaming response, so re-fetch with fetch API
        // The XHR was for progress; now make the actual streaming request
        const streamResp = await fetch(`${API_BASE_URL}/runs/stream`, {
          method: "POST",
          body: formData,
          signal: abort.signal,
        });

        if (!streamResp.ok) {
          const err = await streamResp.json().catch(() => ({ error: streamResp.statusText }));
          throw new Error(err.error || `HTTP ${streamResp.status}`);
        }

        processSSEStream(streamResp);
      } catch (e: unknown) {
        if ((e as Error).name === "AbortError") return;
        setStatus("error");
        setError((e as Error).message);
        setUploadProgress(null);
      }
    },
    [reset]
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setStatus("idle");
    setUploadProgress(null);
  }, []);

  function processSSEStream(resp: Response) {
    const reader = resp.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    // Persist across chunks — SSE messages may span multiple read() calls
    let currentEvent = "";
    let currentData = "";

    setStatus("running");

    function dispatch() {
      if (currentEvent && currentData) {
        try {
          const parsed = JSON.parse(currentData);
          handleSSEEvent(currentEvent, parsed);
        } catch {
          // skip malformed JSON
        }
      }
      currentEvent = "";
      currentData = "";
    }

    function read(): void {
      reader.read().then(({ done, value }) => {
        if (done) {
          dispatch(); // flush any remaining event
          setStatus((prev) => (prev === "running" ? "completed" : prev));
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const rawLine of lines) {
          const line = rawLine.replace(/\r$/, ""); // strip \r from \r\n

          if (line.startsWith("event:")) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            currentData = line.slice(5).trim();
          } else if (line === "") {
            dispatch();
          }
        }

        read();
      });
    }

    read();
  }

  function handleSSEEvent(eventType: string, data: Record<string, unknown>) {
    const sseEvent = { event: eventType, data } as SSEEvent;
    appendEvent(sseEvent);

    switch (eventType) {
      case "run_started":
        setRunId(data.run_id as string);
        break;

      case "tool_call": {
        const node = data.tool as string;
        setSteps((prev) =>
          prev.map((s) =>
            s.node === node
              ? { ...s, status: "running", inputs: data.inputs as Record<string, unknown> }
              : s
          )
        );
        break;
      }

      case "tool_result": {
        const node = data.tool as string;
        setSteps((prev) =>
          prev.map((s) =>
            s.node === node
              ? { ...s, status: "completed", outputs: data.outputs as Record<string, unknown> }
              : s
          )
        );
        break;
      }

      case "invoice_result": {
        // Backend sends { invoice: { ... } }
        const invoice = (data.invoice ?? data) as unknown as InvoiceResult;
        setInvoices((prev) => [...prev, invoice]);
        break;
      }

      case "final_result": {
        // Backend sends { result: { ... } }
        const result = (data.result ?? data) as unknown as FinalResult;
        setFinalResult(result);
        setStatus("completed");
        break;
      }

      case "error":
        setError(data.error as string);
        setStatus("error");
        break;
    }
  }

  return {
    status,
    runId,
    steps,
    invoices,
    finalResult,
    error,
    events,
    uploadProgress,
    startRunWithFolder,
    startRunWithFiles,
    cancel,
    reset,
  };
}
