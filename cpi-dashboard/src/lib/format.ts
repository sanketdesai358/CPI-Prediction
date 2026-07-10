export function formatMonth(month: string): string {
  const [year, rawMonth] = month.split("-").map(Number);
  return new Intl.DateTimeFormat("en-US", { month: "short", year: "numeric", timeZone: "UTC" }).format(
    new Date(Date.UTC(year, rawMonth - 1, 1))
  );
}

export function formatPercent(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatPp(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${value >= 0 ? "+" : ""}${value.toFixed(digits)} pp`;
}

export function formatIndex(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return value.toFixed(3);
}

export function formatWeight(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${value.toFixed(3)}%`;
}

export function signedClass(value: number | null | undefined): string {
  if (value === null || value === undefined) return "text-muted";
  if (value > 0) return "text-rose";
  if (value < 0) return "text-teal";
  return "text-muted";
}
