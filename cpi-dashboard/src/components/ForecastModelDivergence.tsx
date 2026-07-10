"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type {
  ChallengerCurrentForecast,
  ChallengerMajorComponentRow,
  ChallengerMajorComponentSeriesRow,
  ChallengerResult,
  ChallengerVariant,
  ComponentEntry,
  ForecastRun
} from "@/lib/types";
import { formatMonth, formatPercent, formatWeight } from "@/lib/format";

const currentModelKeys = ["hrnn", "iGru", "seasonalAr", "productionTier1", "productionTier3"] as const;
const historyModelKeys = ["production", "productionTier1", "productionTier3", "hrnn", "iGru", "seasonalAr"] as const;

const modelLabels: Record<ChallengerVariant, string> = {
  production: "Legacy proxy (not full model)",
  productionTier1: "Tier 1 fallback",
  productionTier3: "Tier 3 fallback",
  hrnn: "HRNN",
  iGru: "I-GRU",
  seasonalAr: "Seasonal AR"
};

const modelColors: Record<ChallengerVariant, string> = {
  production: "#64748b",
  productionTier1: "#0ea5e9",
  productionTier3: "#dc2626",
  hrnn: "#0f766e",
  iGru: "#7c3aed",
  seasonalAr: "#f59e0b"
};

type MajorProductionAggregate = {
  saMm: number | null;
  nsaMm: number | null;
  weight: number | null;
  componentCount: number;
};

type CurrentForecastRow = ChallengerCurrentForecast["rows"][number];
type CurrentMajorRow = NonNullable<ChallengerCurrentForecast["majorRows"]>[number];
type CurrentComponentRow = NonNullable<ChallengerCurrentForecast["componentRows"]>[number];

function signedPercent(value: number | null | undefined, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  const scaled = value * 100;
  return `${scaled >= 0 ? "+" : ""}${scaled.toFixed(digits)}%`;
}

function compactMonth(month: string) {
  return formatMonth(month).replace(" ", "\n");
}

function isUnderMajor(itemCode: string, majorCode: string, byCode: Map<string, ComponentEntry>) {
  if (majorCode === "SAT1" && itemCode === "SETB01") return false;
  if (itemCode === majorCode) return true;
  let cursor = byCode.get(itemCode);
  while (cursor?.parent) {
    if (cursor.parent === majorCode) return true;
    cursor = byCode.get(cursor.parent);
  }
  return false;
}

function isInSpecialMajor(itemCode: string, majorCode: string) {
  if (majorCode !== "SA0E") return false;
  return itemCode.startsWith("SETB") || itemCode === "SEHE" || itemCode.startsWith("SEHF");
}

function aggregateProductionMajors(
  forecast: ForecastRun,
  entries: ComponentEntry[],
  diagnostics: ChallengerMajorComponentRow[]
): Record<string, MajorProductionAggregate> {
  const byCode = new Map(entries.map((entry) => [entry.itemCode, entry]));
  const out: Record<string, MajorProductionAggregate> = {};
  for (const major of diagnostics) {
    const direct = forecast.components.find((component) => component.itemCode === major.itemCode);
    const components = direct
      ? [direct]
      : forecast.components.filter(
          (component) => isUnderMajor(component.itemCode, major.itemCode, byCode) || isInSpecialMajor(component.itemCode, major.itemCode)
        );
    let weightSum = 0;
    let saSum = 0;
    let nsaSum = 0;
    for (const component of components) {
      const weight = component.blsCurrentRi ?? byCode.get(component.itemCode)?.currentRi ?? 0;
      if (!Number.isFinite(weight) || weight <= 0) continue;
      weightSum += weight;
      saSum += weight * component.forecast_sa_mm;
      nsaSum += weight * component.forecast_nsa_mm;
    }
    out[major.itemCode] = {
      saMm: weightSum ? saSum / weightSum : null,
      nsaMm: weightSum ? nsaSum / weightSum : null,
      weight: major.weight,
      componentCount: components.length
    };
  }
  return out;
}

function hasProductionAggregate(row: ChallengerMajorComponentRow, productionMajors: Record<string, MajorProductionAggregate>) {
  return (productionMajors[row.itemCode]?.componentCount ?? 0) > 0;
}

function measureValue(
  row: CurrentForecastRow | CurrentMajorRow | CurrentComponentRow | undefined,
  model: ChallengerVariant,
  measure: "saMm" | "nsaMm" | "saYoy" | "nsaYoy"
) {
  return row?.[model]?.[measure] ?? null;
}

function ChallengerDelta({ production, value }: { production: number | null; value: number | null }) {
  return (
    <span className="block text-xs text-muted">
      delta {production === null || value === null ? "n/a" : signedPercent(value - production)}
    </span>
  );
}

export function ForecastModelDivergence({
  forecast,
  challenger,
  entries
}: {
  forecast: ForecastRun;
  challenger: ChallengerResult | null;
  entries: ComponentEntry[];
}) {
  const current = challenger?.currentForecast ?? null;
  const diagnostics = challenger?.majorComponentDiagnostics ?? [];
  const majorSeries = challenger?.majorComponentSeries ?? {};
  const productionMajors = useMemo(
    () => aggregateProductionMajors(forecast, entries, diagnostics),
    [forecast, entries, diagnostics]
  );
  const diagnosticsWithProduction = diagnostics.filter((row) => hasProductionAggregate(row, productionMajors));
  return (
    <div className="grid gap-4">
      <section className="rounded border border-line bg-white p-4 shadow-subtle">
        <h2 className="mb-2 text-base font-semibold">Current forecast month: your model vs challengers</h2>
        <p className="mb-3 text-sm text-muted">
          Your model is the production forecast in <span className="font-mono">latest-forecast.json</span>, including the current feed inputs and fallbacks.
          Challenger columns are research outputs for the same forecast month.
        </p>
        <CurrentHeadlineCoreTable current={current} />
      </section>
      <section className="rounded border border-line bg-white p-4 shadow-subtle">
        <h2 className="mb-2 text-base font-semibold">Tracked component divergence for {formatMonth(forecast.forecastMonth)}</h2>
        <p className="mb-3 text-sm text-muted">
          Production tracked-component values are aggregated from your current component forecast rows using BLS relative-importance weights where the
          dashboard hierarchy or an explicit code group is available.
          Delta is challenger minus your production model.
        </p>
        <MajorCurrentDivergenceTable current={current} diagnostics={diagnosticsWithProduction} productionMajors={productionMajors} />
      </section>
      <section className="rounded border border-line bg-white p-4 shadow-subtle">
        <h2 className="mb-2 text-base font-semibold">All production component discrepancies</h2>
        <p className="mb-3 text-sm text-muted">
          Every component in the production-ready forecast artifact, sorted by the largest absolute SA m/m gap versus any challenger/fallback model.
        </p>
        <AllProductionComponentsTable current={current} />
      </section>
      <section className="rounded border border-line bg-white p-4 shadow-subtle">
        <h2 className="mb-2 text-base font-semibold">Historical divergence tracker</h2>
        <p className="mb-3 text-sm text-muted">
          Full historical live-feed production replay is not available in the stored artifacts, so the history below tracks true walk-forward challenger/fallback
          errors against actual CPI. The gray legacy proxy is labeled separately because it is not your full production model.
        </p>
        <MajorHistoryChart diagnostics={diagnosticsWithProduction} series={majorSeries} />
      </section>
    </div>
  );
}

function CurrentHeadlineCoreTable({ current }: { current: ChallengerCurrentForecast | null }) {
  if (!current?.rows?.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No current challenger comparison has been generated yet.</div>;
  }
  const measures = [
    ["saMm", "SA m/m"],
    ["nsaMm", "NSA m/m"],
    ["saYoy", "SA y/y"],
    ["nsaYoy", "NSA y/y"]
  ] as const;
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase text-muted">
          <tr>
            <th className="py-2 pr-4">Series</th>
            <th className="py-2 pr-4">Measure</th>
            <th className="py-2 pr-4">Your production model</th>
            {currentModelKeys.map((model) => (
              <th key={model} className="py-2 pr-4">{modelLabels[model]}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {current.rows.flatMap((row) =>
            measures.map(([measure, label]) => {
              const production = row.production[measure];
              return (
                <tr key={`${row.series}-${measure}`} className="border-b border-line/70 align-top">
                  <td className="py-2 pr-4 font-medium">{row.label}</td>
                  <td className="py-2 pr-4 text-muted">{label}</td>
                  <td className="py-2 pr-4 font-semibold">{formatPercent(production, 3)}</td>
                  {currentModelKeys.map((model) => {
                    const value = measureValue(row, model, measure);
                    return (
                      <td key={model} className="py-2 pr-4">
                        {formatPercent(value, 3)}
                        <ChallengerDelta production={production} value={value} />
                      </td>
                    );
                  })}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

function MajorCurrentDivergenceTable({
  current,
  diagnostics,
  productionMajors
}: {
  current: ChallengerCurrentForecast | null;
  diagnostics: ChallengerMajorComponentRow[];
  productionMajors: Record<string, MajorProductionAggregate>;
}) {
  const currentByCode = new Map((current?.majorRows ?? []).map((row) => [row.series, row]));
  if (!diagnostics.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No major-component diagnostics have been generated yet.</div>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase text-muted">
          <tr>
            <th className="py-2 pr-4">Component</th>
            <th className="py-2 pr-4">Weight</th>
            <th className="py-2 pr-4">Your production model</th>
            {currentModelKeys.map((model) => (
              <th key={model} className="py-2 pr-4">{modelLabels[model]}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {diagnostics.map((diagnostic) => {
            const production = productionMajors[diagnostic.itemCode];
            const currentRow = currentByCode.get(diagnostic.itemCode);
            const productionSa = production?.saMm ?? null;
            return (
              <tr key={diagnostic.itemCode} className="border-b border-line/70 align-top">
                <td className="min-w-[220px] py-3 pr-4">
                  <div className="font-medium">{diagnostic.name}</div>
                  <div className="text-xs text-muted">{diagnostic.itemCode}</div>
                </td>
                <td className="py-3 pr-4">{formatWeight(diagnostic.weight)}</td>
                <td className="py-3 pr-4">
                  <div className="font-semibold">SA {formatPercent(productionSa, 3)}</div>
                  <div className="text-xs text-muted">NSA {formatPercent(production?.nsaMm ?? null, 3)}</div>
                  <div className="text-xs text-muted">{production?.componentCount ?? 0} forecast rows</div>
                </td>
                {currentModelKeys.map((model) => {
                  const value = measureValue(currentRow, model, "saMm");
                  const nsa = measureValue(currentRow, model, "nsaMm");
                  const mae = diagnostic.windowC[model]?.saMmMae ?? null;
                  return (
                    <td key={model} className="min-w-[150px] py-3 pr-4">
                      <div className="font-medium">SA {formatPercent(value, 3)}</div>
                      <ChallengerDelta production={productionSa} value={value} />
                      <div className="text-xs text-muted">NSA {formatPercent(nsa, 3)}</div>
                      <div className="text-xs text-muted">Hist MAE {formatPercent(mae, 3)}</div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AllProductionComponentsTable({ current }: { current: ChallengerCurrentForecast | null }) {
  const [sort, setSort] = useState<"weightedGap" | "maxDelta" | "weight" | "productionSa" | "hrnnDelta" | "iGruDelta" | "seasonalArDelta" | "tier1Delta" | "tier3Delta">("weightedGap");
  const rows = useMemo(() => {
    return [...(current?.componentRows ?? [])]
      .map((row) => {
        const production = row.production.saMm;
        const deltas = {
          hrnnDelta: production === null || row.hrnn.saMm === null ? null : row.hrnn.saMm - production,
          iGruDelta: production === null || row.iGru.saMm === null ? null : row.iGru.saMm - production,
          seasonalArDelta: production === null || row.seasonalAr.saMm === null ? null : row.seasonalAr.saMm - production,
          tier1Delta: production === null || row.productionTier1?.saMm === null || row.productionTier1?.saMm === undefined ? null : row.productionTier1.saMm - production,
          tier3Delta: production === null || row.productionTier3?.saMm === null || row.productionTier3?.saMm === undefined ? null : row.productionTier3.saMm - production
        };
        const maxDelta = Math.max(...Object.values(deltas).map((value) => (value === null ? 0 : Math.abs(value))));
        const weightedGap = (row.weight ?? 0) * maxDelta;
        return { ...row, ...deltas, maxDelta, weightedGap };
      })
      .sort((a, b) => {
        if (sort === "weight") return (b.weight ?? 0) - (a.weight ?? 0);
        if (sort === "productionSa") return Math.abs(b.production.saMm ?? 0) - Math.abs(a.production.saMm ?? 0);
        return Math.abs(Number(b[sort] ?? 0)) - Math.abs(Number(a[sort] ?? 0));
      });
  }, [current, sort]);
  if (!rows.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No per-component challenger comparison has been generated yet.</div>;
  }
  const modelColumns = [
    ["hrnn", "HRNN", "hrnnDelta"],
    ["iGru", "I-GRU", "iGruDelta"],
    ["seasonalAr", "Seasonal AR", "seasonalArDelta"],
    ["productionTier1", "Tier 1 fallback", "tier1Delta"],
    ["productionTier3", "Tier 3 fallback", "tier3Delta"]
  ] as const;
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        {[
          ["weightedGap", "Largest weighted gap"],
          ["maxDelta", "Largest raw gap"],
          ["weight", "Weight"],
          ["productionSa", "Production move"],
          ["hrnnDelta", "HRNN gap"],
          ["iGruDelta", "I-GRU gap"],
          ["seasonalArDelta", "Seasonal AR gap"],
          ["tier1Delta", "Tier 1 gap"],
          ["tier3Delta", "Tier 3 gap"]
        ].map(([key, label]) => (
          <button
            key={key}
            className={`rounded border px-3 py-1 text-sm ${sort === key ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setSort(key as typeof sort)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="max-h-[720px] overflow-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="sticky top-0 z-10 border-b border-line bg-white text-xs uppercase text-muted">
            <tr>
              <th className="py-2 pr-4">Component</th>
              <th className="py-2 pr-4">Tier/model</th>
              <th className="py-2 pr-4">Weight</th>
              <th className="py-2 pr-4">Your production model</th>
              <th className="py-2 pr-4">Weighted gap</th>
              <th className="py-2 pr-4">Largest gap</th>
              {modelColumns.map(([, label]) => (
                <th key={label} className="py-2 pr-4">{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.series} className="border-b border-line/70 align-top">
                <td className="min-w-[240px] py-3 pr-4">
                  <div className="font-medium">{row.label}</div>
                  <div className="text-xs text-muted">{row.series}</div>
                </td>
                <td className="min-w-[180px] py-3 pr-4 text-xs text-muted">
                  <div>Tier {row.tier ?? "n/a"}</div>
                  <div>{row.modelType ?? "n/a"}</div>
                </td>
                <td className="py-3 pr-4">{formatWeight(row.weight)}</td>
                <td className="py-3 pr-4">
                  <div className="font-semibold">SA {formatPercent(row.production.saMm, 3)}</div>
                  <div className="text-xs text-muted">NSA {formatPercent(row.production.nsaMm, 3)}</div>
                </td>
                <td className="py-3 pr-4 font-semibold">{row.weightedGap.toFixed(3)} pp</td>
                <td className="py-3 pr-4">{signedPercent(row.maxDelta)}</td>
                {modelColumns.map(([model, , deltaKey]) => {
                  const value = measureValue(row, model, "saMm");
                  const delta = row[deltaKey];
                  return (
                    <td key={model} className="min-w-[150px] py-3 pr-4">
                      <div>{formatPercent(value, 3)}</div>
                      <div className="text-xs text-muted">delta {signedPercent(delta)}</div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-muted">
        Gaps are challenger/fallback SA m/m minus your production model SA m/m. The table includes all {rows.length} current production forecast components.
      </p>
    </div>
  );
}

function MajorHistoryChart({
  diagnostics,
  series
}: {
  diagnostics: ChallengerMajorComponentRow[];
  series: Record<string, ChallengerMajorComponentSeriesRow[]>;
}) {
  const available = diagnostics.filter((row) => (series[row.itemCode] ?? []).length);
  const [component, setComponent] = useState(available[0]?.itemCode ?? "");
  const [basis, setBasis] = useState<"Sa" | "Nsa">("Sa");
  const [range, setRange] = useState<"all" | "2022" | "5y">("2022");
  const [enabled, setEnabled] = useState<Record<(typeof historyModelKeys)[number], boolean>>({
    production: false,
    productionTier1: true,
    productionTier3: true,
    hrnn: true,
    iGru: true,
    seasonalAr: true
  });
  const rows = series[component] ?? [];
  const data = useMemo(() => {
    const cutoff = range === "2022" ? "2022-01" : range === "5y" ? "2021-06" : "0000-00";
    const actualKey = `actual${basis}Mm`;
    return rows
      .filter((row) => row.month >= cutoff)
      .map((row) => {
        const item: Record<string, number | string | null> = { month: row.month };
        const actual = row[actualKey];
        for (const model of historyModelKeys) {
          const value = row[`${model}${basis}Mm`];
          item[model] =
            typeof value === "number" && typeof actual === "number"
              ? (value - actual) * 100
              : null;
        }
        return item;
      });
  }, [basis, range, rows]);
  if (!available.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No historical major-component series exists in the challenger artifact yet.</div>;
  }
  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        <select className="rounded border border-line bg-white px-3 py-2 text-sm" value={component} onChange={(event) => setComponent(event.target.value)}>
          {available.map((row) => (
            <option key={row.itemCode} value={row.itemCode}>{row.name}</option>
          ))}
        </select>
        {(["Sa", "Nsa"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-2 text-sm ${basis === item ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setBasis(item)}
          >
            {item === "Sa" ? "SA" : "NSA"} error
          </button>
        ))}
        {(["2022", "5y", "all"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-2 text-sm ${range === item ? "border-sky bg-sky text-white" : "border-line bg-white"}`}
            onClick={() => setRange(item)}
          >
            {item === "2022" ? "2022-present" : item === "5y" ? "Last 5y" : "Full span"}
          </button>
        ))}
        {historyModelKeys.map((model) => (
          <label key={model} className="flex items-center gap-2 rounded border border-line bg-white px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={enabled[model]}
              onChange={(event) => setEnabled((current) => ({ ...current, [model]: event.target.checked }))}
            />
            <span style={{ color: modelColors[model] }}>{modelLabels[model]}</span>
          </label>
        ))}
      </div>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
            <CartesianGrid stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
            <YAxis width={58} tickFormatter={(value) => `${Number(value).toFixed(2)}%`} />
            <Tooltip
              labelFormatter={(label) => formatMonth(String(label))}
              formatter={(value, name) => [`${Number(value).toFixed(3)}%`, String(name)]}
            />
            <ReferenceLine y={0} stroke="#94a3b8" />
            <Legend />
            {historyModelKeys.map((model) =>
              enabled[model] ? (
                <Line
                  key={model}
                  type="monotone"
                  dataKey={model}
                  name={modelLabels[model]}
                  stroke={modelColors[model]}
                  strokeWidth={model === "production" ? 1.2 : 1.8}
                  dot={false}
                  isAnimationActive={false}
                  connectNulls={false}
                />
              ) : null
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 text-xs text-muted">Error is model prediction minus actual CPI m/m, in percentage points.</div>
    </div>
  );
}
