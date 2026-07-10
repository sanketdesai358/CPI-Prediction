import type { ComponentEntry, SeriesPoint } from "./types";

export function valueForMode(point: SeriesPoint, mode: "mm" | "yoy"): number | null {
  return mode === "mm" ? point.saMm : point.nsaYoy;
}

export function historyForMonths(entry: ComponentEntry, months: string[]): SeriesPoint[] {
  const byMonth = new Map(entry.history.map((point) => [point.month, point]));
  return months.map((month) => byMonth.get(month)).filter((point): point is SeriesPoint => Boolean(point));
}

export function contributionResidual(rows: ComponentEntry[], headlineMm: number | null, month: string): number | null {
  if (headlineMm === null) return null;
  let sum = 0;
  let used = 0;
  for (const entry of rows) {
    const point = entry.history.find((item) => item.month === month);
    if (point?.contribution !== null && point?.contribution !== undefined) {
      sum += point.contribution;
      used += 1;
    }
  }
  if (!used) return null;
  return headlineMm * 100 - sum;
}
