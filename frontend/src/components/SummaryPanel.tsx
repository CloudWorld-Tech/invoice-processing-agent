import { DollarSign, FileText, PieChart, AlertTriangle, Flag } from "lucide-react";
import { memo } from "react";
import type { FinalResult } from "../types";
import { formatCurrency } from "../utils/formatters";

interface Props {
  result: FinalResult;
}

const CATEGORY_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
  "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
];

export const SummaryPanel = memo(function SummaryPanel({ result }: Props) {
  const categories = result.spend_by_category ?? [];
  const notes = result.issues_and_assumptions ?? [];
  const flags = result.flags ?? [];
  const maxSpend = categories.length > 0
    ? Math.max(...categories.map((c) => c.total))
    : 1;

  return (
    <div className="summary-panel" aria-label="Run Summary">
      <h2>Run Summary</h2>

      <div className="summary-cards" role="list">
        <div className="summary-card" role="listitem">
          <div className="card-icon" style={{ backgroundColor: "#3b82f620", color: "#3b82f6" }}>
            <FileText size={20} aria-hidden="true" />
          </div>
          <div className="card-content">
            <span className="card-value">{result.invoice_count}</span>
            <span className="card-label">Invoices</span>
          </div>
        </div>
        <div className="summary-card" role="listitem">
          <div className="card-icon" style={{ backgroundColor: "#10b98120", color: "#10b981" }}>
            <DollarSign size={20} aria-hidden="true" />
          </div>
          <div className="card-content">
            <span className="card-value">{formatCurrency(result.total_spend)}</span>
            <span className="card-label">Total Spend</span>
          </div>
        </div>
        <div className="summary-card" role="listitem">
          <div className="card-icon" style={{ backgroundColor: "#8b5cf620", color: "#8b5cf6" }}>
            <PieChart size={20} aria-hidden="true" />
          </div>
          <div className="card-content">
            <span className="card-value">{categories.length}</span>
            <span className="card-label">Categories</span>
          </div>
        </div>
        {notes.length > 0 && (
          <div className="summary-card" role="listitem">
            <div className="card-icon" style={{ backgroundColor: "#f59e0b20", color: "#f59e0b" }}>
              <AlertTriangle size={20} aria-hidden="true" />
            </div>
            <div className="card-content">
              <span className="card-value">{notes.length}</span>
              <span className="card-label">Notes</span>
            </div>
          </div>
        )}
        {flags.length > 0 && (
          <div className="summary-card" role="listitem">
            <div className="card-icon" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
              <Flag size={20} aria-hidden="true" />
            </div>
            <div className="card-content">
              <span className="card-value">{flags.length}</span>
              <span className="card-label">Flags</span>
            </div>
          </div>
        )}
      </div>

      {categories.length > 0 && (
        <div className="category-breakdown">
          <h3>Spend by Category</h3>
          <div className="category-bars">
            {[...categories]
              .sort((a, b) => b.total - a.total)
              .map((cat, i) => (
                <div key={cat.category} className="category-bar-row">
                  <div className="category-bar-label">
                    <span className="category-name">{cat.category}</span>
                    <span className="category-amount">
                      {formatCurrency(cat.total)} ({cat.count})
                    </span>
                  </div>
                  <div className="category-bar-track" role="progressbar" aria-valuenow={cat.total} aria-valuemax={maxSpend} aria-label={`${cat.category} spend`}>
                    <div
                      className="category-bar-fill"
                      style={{
                        width: `${(cat.total / maxSpend) * 100}%`,
                        backgroundColor: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {notes.length > 0 && (
        <div className="issues-section">
          <h3>Issues &amp; Assumptions</h3>
          <ul aria-label="Issues and assumptions list">
            {notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {flags.length > 0 && (
        <div className="flags-section">
          <h3>Flags</h3>
          <ul aria-label="Flags list">
            {flags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
});
