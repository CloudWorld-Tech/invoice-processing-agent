import { FileText } from "lucide-react";
import { memo } from "react";
import type { RunStatus } from "../types";

interface Props {
  status: RunStatus;
  runId: string | null;
}

const STATUS_COLORS: Record<RunStatus, string> = {
  idle: "#6b7280",
  connecting: "#f59e0b",
  running: "#3b82f6",
  completed: "#10b981",
  error: "#ef4444",
};

export const Header = memo(function Header({ status, runId }: Props) {
  return (
    <header className="header" role="banner">
      <div className="header-left">
        <FileText size={28} aria-hidden="true" />
        <div>
          <h1>Invoice Processing Agent</h1>
          <p className="subtitle">AI-powered invoice extraction &amp; categorization</p>
        </div>
      </div>
      <div className="header-right">
        <span
          className="status-badge"
          style={{ backgroundColor: STATUS_COLORS[status] }}
          role="status"
          aria-label={`Status: ${status}`}
        >
          {status.toUpperCase()}
        </span>
        {runId && <span className="run-id">Run: {runId.slice(0, 8)}...</span>}
      </div>
    </header>
  );
});
