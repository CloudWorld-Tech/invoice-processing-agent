import { Terminal } from "lucide-react";
import { memo, useEffect, useRef } from "react";
import type { SSEEvent } from "../types";

interface Props {
  events: SSEEvent[];
}

const EVENT_COLORS: Record<string, string> = {
  run_started: "#3b82f6",
  progress: "#8b5cf6",
  tool_call: "#f59e0b",
  tool_result: "#10b981",
  invoice_result: "#06b6d4",
  final_result: "#10b981",
  error: "#ef4444",
};

export const EventLog = memo(function EventLog({ events }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="event-log" role="log" aria-label="SSE Event Log" aria-live="polite">
      <h2>
        <Terminal size={16} aria-hidden="true" />
        SSE Event Log ({events.length})
      </h2>
      <div className="event-log-scroll" ref={scrollRef}>
        {events.length === 0 && (
          <p className="event-log-empty">Events will appear here during processing...</p>
        )}
        {events.map((evt, i) => (
          <div key={i} className="event-entry" style={{ contentVisibility: "auto" }}>
            <span
              className="event-type"
              style={{ color: EVENT_COLORS[evt.event] || "#9ca3af" }}
            >
              {evt.event}
            </span>
            <span className="event-data">
              {JSON.stringify(evt.data, null, 0).slice(0, 200)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
});
