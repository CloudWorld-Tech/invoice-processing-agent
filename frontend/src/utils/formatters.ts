export function formatCurrency(n: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(n);
}

export function confidenceColor(c: number): string {
  if (c >= 0.8) return "#10b981";
  if (c >= 0.5) return "#f59e0b";
  return "#ef4444";
}

export function confidenceLabel(c: number): string {
  if (c >= 0.8) return "High";
  if (c >= 0.5) return "Medium";
  return "Low";
}
