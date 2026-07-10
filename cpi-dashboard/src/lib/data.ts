import "server-only";

import cache from "@/data/dashboard-cache.json";
import extendedRegistryJson from "@/data/extended-registry.json";
import forecastJson from "@/data/forecast/latest-forecast.json";
import feedHealthJson from "@/data/forecast/feed-health.json";
import scoreJson from "@/data/forecast/latest-score.json";
import backtestAJson from "@/data/forecast/backtest-A.json";
import backtestBJson from "@/data/forecast/backtest-B.json";
import backtestCJson from "@/data/forecast/backtest-C.json";
import challengerJson from "@/data/challenger/results.json";
import modelComparisonJson from "@/data/challenger/model-comparison.json";
import registryJson from "@/data/registry.json";
import type { BacktestResult, ChallengerResult, ComponentEntry, DashboardCache, FeedHealth, ForecastRun, ModelComparisonResult, RegistryEntry, ScoreResult } from "./types";

const dashboardCache = cache as DashboardCache;
const registry = registryJson as RegistryEntry[];
const extendedRegistry = extendedRegistryJson as Array<RegistryEntry & {
  tier?: number | null;
  model_type?: string;
  input_series?: string[];
  pass_through_lags?: number[];
  event_calendar?: string[];
  model_weight?: number | null;
  bls_current_ri?: number | null;
  stats?: Record<string, number | null>;
}>;
const forecast = forecastJson as ForecastRun;
const feedHealth = feedHealthJson as FeedHealth;
const score = scoreJson as ScoreResult;
const challenger = challengerJson as ChallengerResult;
const modelComparison = modelComparisonJson as ModelComparisonResult;
const backtests = {
  A: backtestAJson as BacktestResult,
  B: backtestBJson as BacktestResult,
  C: backtestCJson as BacktestResult
};

export function getDashboardData(): DashboardCache {
  return dashboardCache;
}

export function getRegistry(): RegistryEntry[] {
  return registry;
}

export function getExtendedRegistry() {
  return extendedRegistry;
}

export function getForecast(): ForecastRun | null {
  return forecast?.forecastMonth ? forecast : null;
}

export function getFeedHealth(): FeedHealth | null {
  return feedHealth?.forecastMonth ? feedHealth : null;
}

export function getScore(): ScoreResult | null {
  return score?.month ? score : null;
}

export function getBacktests(): Record<"A" | "B" | "C", BacktestResult> {
  return backtests;
}

export function getChallenger(): ChallengerResult | null {
  return challenger?.status ? challenger : null;
}

export function getModelComparison(): ModelComparisonResult | null {
  return modelComparison?.rows?.length ? modelComparison : null;
}

export function getModelMeta(itemCode: string) {
  return extendedRegistry.find((entry) => entry.item_code === itemCode);
}

export function getForecastComponent(itemCode: string) {
  return forecast?.components?.find((entry) => entry.itemCode === itemCode);
}

export function getComponent(itemCode: string): ComponentEntry | undefined {
  return dashboardCache.entries.find((entry) => entry.itemCode === itemCode);
}

export function getChildren(itemCode: string): ComponentEntry[] {
  return dashboardCache.entries.filter((entry) => entry.parent === itemCode);
}

export function getTopLevelComponents(): ComponentEntry[] {
  return dashboardCache.entries.filter((entry) => entry.parent === "SA0" || entry.level === 0);
}

export function getMethodologyRows(): ComponentEntry[] {
  return dashboardCache.entries.filter((entry) => {
    return (
      entry.level <= 2 ||
      entry.formula !== "aggregate" ||
      Boolean(entry.altData) ||
      entry.itemCode.startsWith("SE")
    );
  });
}

export function componentHref(itemCode: string): string {
  return `/components/${encodeURIComponent(itemCode)}`;
}

export function sortByWeight(entries: ComponentEntry[]): ComponentEntry[] {
  return [...entries].sort((a, b) => (b.currentRi ?? -1) - (a.currentRi ?? -1));
}
