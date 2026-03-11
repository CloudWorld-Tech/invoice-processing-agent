import { ArrowUpDown, Download } from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import type { InvoiceResult, SortDirection, SortField } from "../types";
import { confidenceColor, confidenceLabel, formatCurrency } from "../utils/formatters";

interface Props {
  invoices: InvoiceResult[];
}

function compareInvoices(a: InvoiceResult, b: InvoiceResult, field: SortField, dir: SortDirection): number {
  let cmp = 0;
  switch (field) {
    case "vendor":
      cmp = a.vendor.localeCompare(b.vendor);
      break;
    case "invoice_date":
      cmp = a.invoice_date.localeCompare(b.invoice_date);
      break;
    case "total":
      cmp = a.total - b.total;
      break;
    case "category":
      cmp = a.category.localeCompare(b.category);
      break;
    case "confidence":
      cmp = a.confidence - b.confidence;
      break;
  }
  return dir === "asc" ? cmp : -cmp;
}

function exportCSV(invoices: InvoiceResult[]) {
  const headers = ["Vendor", "Date", "Invoice #", "Total", "Category", "Confidence"];
  const rows = invoices.map((inv) => [
    `"${inv.vendor.replace(/"/g, '""')}"`,
    inv.invoice_date,
    inv.invoice_number || "",
    inv.total.toFixed(2),
    `"${inv.category.replace(/"/g, '""')}"`,
    (inv.confidence * 100).toFixed(0) + "%",
  ]);
  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "invoices.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function exportJSON(invoices: InvoiceResult[]) {
  const blob = new Blob([JSON.stringify(invoices, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "invoices.json";
  a.click();
  URL.revokeObjectURL(url);
}

export const InvoiceTable = memo(function InvoiceTable({ invoices }: Props) {
  const [sortField, setSortField] = useState<SortField>("vendor");
  const [sortDir, setSortDir] = useState<SortDirection>("asc");

  const toggleSort = useCallback((field: SortField) => {
    setSortField((prev) => {
      if (prev === field) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortDir("asc");
      }
      return field;
    });
  }, []);

  const sorted = useMemo(
    () => [...invoices].sort((a, b) => compareInvoices(a, b, sortField, sortDir)),
    [invoices, sortField, sortDir]
  );

  if (invoices.length === 0) return null;

  const sortIndicator = (field: SortField) =>
    sortField === field ? (sortDir === "asc" ? " \u25B2" : " \u25BC") : "";

  return (
    <div className="invoice-table-container">
      <div className="table-header-row">
        <h2>Processed Invoices ({invoices.length})</h2>
        <div className="export-buttons">
          <button
            className="btn-export"
            onClick={() => exportCSV(invoices)}
            aria-label="Export invoices as CSV"
            title="Export CSV"
          >
            <Download size={14} /> CSV
          </button>
          <button
            className="btn-export"
            onClick={() => exportJSON(invoices)}
            aria-label="Export invoices as JSON"
            title="Export JSON"
          >
            <Download size={14} /> JSON
          </button>
        </div>
      </div>
      <div className="table-scroll">
        <table className="invoice-table" role="table" aria-label="Processed invoices">
          <thead>
            <tr>
              <th>
                <button className="sort-btn" onClick={() => toggleSort("vendor")} aria-label="Sort by vendor">
                  Vendor{sortIndicator("vendor")} <ArrowUpDown size={12} />
                </button>
              </th>
              <th>
                <button className="sort-btn" onClick={() => toggleSort("invoice_date")} aria-label="Sort by date">
                  Date{sortIndicator("invoice_date")} <ArrowUpDown size={12} />
                </button>
              </th>
              <th>Invoice #</th>
              <th className="text-right">
                <button className="sort-btn sort-btn-right" onClick={() => toggleSort("total")} aria-label="Sort by total">
                  Total{sortIndicator("total")} <ArrowUpDown size={12} />
                </button>
              </th>
              <th>
                <button className="sort-btn" onClick={() => toggleSort("category")} aria-label="Sort by category">
                  Category{sortIndicator("category")} <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="text-center">
                <button className="sort-btn" onClick={() => toggleSort("confidence")} aria-label="Sort by confidence">
                  Confidence{sortIndicator("confidence")} <ArrowUpDown size={12} />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((inv, i) => (
              <tr key={i}>
                <td className="vendor-cell" data-label="Vendor">{inv.vendor}</td>
                <td data-label="Date">{inv.invoice_date}</td>
                <td data-label="Invoice #">{inv.invoice_number || "\u2014"}</td>
                <td className="text-right" data-label="Total">{formatCurrency(inv.total)}</td>
                <td data-label="Category">
                  <span className="category-badge">{inv.category}</span>
                </td>
                <td className="text-center" data-label="Confidence">
                  <span
                    className="confidence-dot"
                    style={{ backgroundColor: confidenceColor(inv.confidence) }}
                    aria-hidden="true"
                  />
                  <span aria-label={`${confidenceLabel(inv.confidence)} confidence: ${(inv.confidence * 100).toFixed(0)}%`}>
                    {(inv.confidence * 100).toFixed(0)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});
