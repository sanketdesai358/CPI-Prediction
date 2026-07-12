import type { ComponentEntry, SeriesPoint } from "./types";

export type TrendGroup =
  | "Housing"
  | "Food"
  | "Transportation"
  | "Medical care"
  | "Household and utilities"
  | "Recreation and education"
  | "Other goods and services";

export type TrendSort =
  | "weightDesc"
  | "latestDesc"
  | "latestAsc"
  | "accelerationDesc"
  | "accelerationAsc"
  | "alpha";

export type TrendConfig = {
  displayName: string;
  itemCode: string;
  group: TrendGroup;
  defaultRank: number;
  precision: number;
  requestedName?: string;
  proxyNote?: string;
};

export type TrendPoint = {
  month: string;
  nsaIndex: number | null;
  yoy: number | null;
  weight: number | null;
};

export type ComponentTrend = {
  config: TrendConfig;
  itemCode: string;
  displayName: string;
  officialName: string;
  seriesId: string;
  group: TrendGroup;
  currentRi: number | null;
  latestMonth: string | null;
  latestYoy: number | null;
  previousMonthYoy: number | null;
  threeMonthChange: number | null;
  twelveMonthChange: number | null;
  tenYearMin: { month: string; value: number } | null;
  tenYearMax: { month: string; value: number } | null;
  tenYearAverage: number | null;
  points: TrendPoint[];
  indexPoints: Array<{ month: string; nsaIndex: number | null }>;
  coverageMonths: number;
  missing: boolean;
};

export const TREND_COMPONENTS: TrendConfig[] = [
  { displayName: "Owners' equivalent rent of residences", itemCode: "SEHC", group: "Housing", defaultRank: 1, precision: 1 },
  { displayName: "Food at home", itemCode: "SAF11", group: "Food", defaultRank: 2, precision: 1 },
  { displayName: "Rent of primary residence", itemCode: "SEHA", group: "Housing", defaultRank: 3, precision: 1 },
  { displayName: "Food away from home", itemCode: "SEFV", group: "Food", defaultRank: 4, precision: 1 },
  { displayName: "Recreation", itemCode: "SAR", group: "Recreation and education", defaultRank: 5, precision: 1 },
  {
    displayName: "Household furnishings and operations",
    itemCode: "SAH3",
    group: "Household and utilities",
    defaultRank: 6,
    precision: 1
  },
  { displayName: "New vehicles", itemCode: "SETA01", group: "Transportation", defaultRank: 7, precision: 1 },
  {
    displayName: "Medical professional services",
    itemCode: "SEMC",
    group: "Medical care",
    defaultRank: 8,
    precision: 1,
    requestedName: "Medical professional services",
    proxyNote: "Mapped to BLS Professional services."
  },
  { displayName: "Household energy", itemCode: "SAH21", group: "Household and utilities", defaultRank: 9, precision: 1 },
  { displayName: "Communication", itemCode: "SAE2", group: "Recreation and education", defaultRank: 10, precision: 1 },
  { displayName: "Motor fuel", itemCode: "SETB", group: "Transportation", defaultRank: 11, precision: 1 },
  { displayName: "Used cars and trucks", itemCode: "SETA02", group: "Transportation", defaultRank: 12, precision: 1 },
  { displayName: "Motor vehicle insurance", itemCode: "SETE", group: "Transportation", defaultRank: 13, precision: 1 },
  { displayName: "Hospital and related services", itemCode: "SEMD", group: "Medical care", defaultRank: 14, precision: 1 },
  { displayName: "Education", itemCode: "SAE1", group: "Recreation and education", defaultRank: 15, precision: 1 },
  { displayName: "Personal care", itemCode: "SAG1", group: "Other goods and services", defaultRank: 16, precision: 1 },
  { displayName: "Apparel", itemCode: "SAA", group: "Other goods and services", defaultRank: 17, precision: 1 },
  { displayName: "Medical care commodities", itemCode: "SAM1", group: "Medical care", defaultRank: 18, precision: 1 },
  { displayName: "Public transportation", itemCode: "SETG", group: "Transportation", defaultRank: 19, precision: 1 },
  { displayName: "Lodging away from home", itemCode: "SEHB", group: "Housing", defaultRank: 20, precision: 1 },
  {
    displayName: "Air fares",
    itemCode: "SETG01",
    group: "Transportation",
    defaultRank: 21,
    precision: 1,
    requestedName: "Air fares",
    proxyNote: "Mapped to BLS Airline fares."
  }
];

export const TREND_GROUPS: TrendGroup[] = [
  "Housing",
  "Food",
  "Transportation",
  "Medical care",
  "Household and utilities",
  "Recreation and education",
  "Other goods and services"
];

function finiteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function calculateYoyPoints(history: SeriesPoint[], weight: number | null, limit = 120): TrendPoint[] {
  const sorted = [...history].sort((a, b) => a.month.localeCompare(b.month));
  const points = sorted.map((point, index) => {
    const prior = sorted[index - 12];
    const yoy =
      finiteNumber(point.nsaIndex) && prior && finiteNumber(prior.nsaIndex) && prior.nsaIndex !== 0
        ? (point.nsaIndex / prior.nsaIndex - 1) * 100
        : null;
    return { month: point.month, nsaIndex: point.nsaIndex, yoy, weight };
  });
  return points.filter((point) => point.month >= (points.find((item) => item.yoy !== null)?.month ?? "9999-99")).slice(-limit);
}

export function pointChange(points: TrendPoint[], monthsBack: number): number | null {
  const latest = [...points].reverse().find((point) => point.yoy !== null);
  if (!latest) return null;
  const latestIndex = points.findIndex((point) => point.month === latest.month);
  const prior = points[latestIndex - monthsBack];
  return finiteNumber(prior?.yoy) ? latest.yoy! - prior.yoy : null;
}

function average(values: number[]): number | null {
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export function buildComponentTrend(config: TrendConfig, entry: ComponentEntry | undefined): ComponentTrend {
  if (!entry) {
    return {
      config,
      itemCode: config.itemCode,
      displayName: config.displayName,
      officialName: config.displayName,
      seriesId: "missing",
      group: config.group,
      currentRi: null,
      latestMonth: null,
      latestYoy: null,
      previousMonthYoy: null,
      threeMonthChange: null,
      twelveMonthChange: null,
      tenYearMin: null,
      tenYearMax: null,
      tenYearAverage: null,
      points: [],
      indexPoints: [],
      coverageMonths: 0,
      missing: true
    };
  }
  const points = calculateYoyPoints(entry.history, entry.currentRi);
  const latest = [...points].reverse().find((point) => finiteNumber(point.yoy)) ?? null;
  const latestIndex = latest ? points.findIndex((point) => point.month === latest.month) : -1;
  const previous = latestIndex > 0 ? points[latestIndex - 1] : null;
  const valid = points.filter((point): point is TrendPoint & { yoy: number } => finiteNumber(point.yoy));
  const min = valid.reduce<typeof valid[number] | null>((best, point) => (!best || point.yoy < best.yoy ? point : best), null);
  const max = valid.reduce<typeof valid[number] | null>((best, point) => (!best || point.yoy > best.yoy ? point : best), null);
  return {
    config,
    itemCode: entry.itemCode,
    displayName: config.displayName,
    officialName: entry.name,
    seriesId: entry.seriesNsa,
    group: config.group,
    currentRi: entry.currentRi,
    latestMonth: latest?.month ?? null,
    latestYoy: latest?.yoy ?? null,
    previousMonthYoy: finiteNumber(previous?.yoy) ? previous.yoy : null,
    threeMonthChange: pointChange(points, 3),
    twelveMonthChange: pointChange(points, 12),
    tenYearMin: min ? { month: min.month, value: min.yoy } : null,
    tenYearMax: max ? { month: max.month, value: max.yoy } : null,
    tenYearAverage: average(valid.map((point) => point.yoy)),
    points,
    indexPoints: entry.history
      .slice()
      .sort((a, b) => a.month.localeCompare(b.month))
      .slice(-120)
      .map((point) => ({ month: point.month, nsaIndex: point.nsaIndex })),
    coverageMonths: valid.length,
    missing: false
  };
}

export function buildComponentTrends(entries: ComponentEntry[], configs = TREND_COMPONENTS): ComponentTrend[] {
  const byCode = new Map(entries.map((entry) => [entry.itemCode, entry]));
  return configs.map((config) => buildComponentTrend(config, byCode.get(config.itemCode)));
}

export function filterComponentTrends(
  trends: ComponentTrend[],
  filters: { search?: string; group?: TrendGroup | "All" }
): ComponentTrend[] {
  const query = filters.search?.trim().toLowerCase() ?? "";
  return trends.filter((trend) => {
    const groupMatch = !filters.group || filters.group === "All" || trend.group === filters.group;
    const queryMatch =
      !query ||
      trend.displayName.toLowerCase().includes(query) ||
      trend.officialName.toLowerCase().includes(query) ||
      trend.itemCode.toLowerCase().includes(query) ||
      trend.seriesId.toLowerCase().includes(query);
    return groupMatch && queryMatch;
  });
}

function sortNumber(value: number | null, fallback: number) {
  return finiteNumber(value) ? value : fallback;
}

export function sortComponentTrends(trends: ComponentTrend[], sort: TrendSort): ComponentTrend[] {
  return [...trends].sort((a, b) => {
    if (sort === "alpha") return a.displayName.localeCompare(b.displayName);
    if (sort === "latestDesc") return sortNumber(b.latestYoy, -Infinity) - sortNumber(a.latestYoy, -Infinity);
    if (sort === "latestAsc") return sortNumber(a.latestYoy, Infinity) - sortNumber(b.latestYoy, Infinity);
    if (sort === "accelerationDesc") return sortNumber(b.threeMonthChange, -Infinity) - sortNumber(a.threeMonthChange, -Infinity);
    if (sort === "accelerationAsc") return sortNumber(a.threeMonthChange, Infinity) - sortNumber(b.threeMonthChange, Infinity);
    return sortNumber(b.currentRi, -Infinity) - sortNumber(a.currentRi, -Infinity);
  });
}

export function selectDisplayTrends(trends: ComponentTrend[], count: 10 | 15 | 20): ComponentTrend[] {
  return trends.slice(0, count);
}

export function trendSummary(trends: ComponentTrend[]) {
  const valid = trends.filter((trend) => finiteNumber(trend.latestYoy));
  const withAcceleration = valid.filter((trend) => finiteNumber(trend.threeMonthChange));
  return {
    highest: sortComponentTrends(valid, "latestDesc")[0] ?? null,
    lowest: sortComponentTrends(valid, "latestAsc")[0] ?? null,
    acceleration: sortComponentTrends(withAcceleration, "accelerationDesc")[0] ?? null,
    deceleration: sortComponentTrends(withAcceleration, "accelerationAsc")[0] ?? null
  };
}
