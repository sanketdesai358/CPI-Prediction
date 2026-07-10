"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { ChallengerCurrentForecast, ChallengerMajorComponentRow, ChallengerResult, ChallengerSeriesRow, ChallengerWindow, ComponentComparisonRow, ModelComparisonModelKey, ModelComparisonResult } from "@/lib/types";
import { formatMonth, formatPercent } from "@/lib/format";

export function ChallengerBanner() {
  return (
    <div className="mb-4 rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900">
      Research comparison - not used in production forecasts.
    </div>
  );
}

function pp(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${(value * 100).toFixed(2)} pp`;
}

function p3(value: number | null | undefined) {
  return formatPercent(value, 3);
}

function compactMonth(month: string) {
  return formatMonth(month).replace(" ", "\n");
}

function modelValueKey(model: ModelComparisonModelKey, measure: "SaMm" | "NsaMm" | "SaYoy" | "NsaYoy" | "SaYoyErrorBp" | "NsaYoyErrorBp") {
  return `${model}${measure}`;
}

const modelDefinitions = [
  {
    label: "HRNN",
    formula: "Hierarchy-aware recurrent challenger",
    note: "Uses component CPI history plus parent/child hierarchy shrinkage in this fast research artifact."
  },
  {
    label: "I-GRU",
    formula: "Independent recurrent challenger",
    note: "Uses each component's own CPI history without hierarchy pooling."
  },
  {
    label: "Production Tier 1 fallback",
    formula: "55% last + 30% trailing3 + 15% seasonal",
    note: "Timeline baseline uses this formula for non-gasoline components; SETB01 gasoline uses EIA gasoline pass-through."
  },
  {
    label: "Production Tier 3 fallback",
    formula: "45% last + 25% trailing3 + 20% seasonal + 10% trailing6",
    note: "Timeline baseline uses this formula for non-gasoline components; SETB01 gasoline uses EIA gasoline pass-through."
  },
  {
    label: "Challenger Seasonal AR",
    formula: "65% seasonal + 35% trailing6",
    note: "Seasonal baseline in the challenger run; seasonal is the same-calendar-month average."
  }
];

export function ChallengerModelDefinitions() {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      {modelDefinitions.map((item) => (
        <div key={item.label} className="rounded border border-line bg-wash p-3">
          <div className="text-sm font-semibold text-ink">{item.label}</div>
          <div className="mt-2 font-mono text-xs text-teal">{item.formula}</div>
          <div className="mt-2 text-xs text-muted">{item.note}</div>
        </div>
      ))}
    </div>
  );
}

export function ChallengerLeagueTable({ rows }: { rows: ComponentComparisonRow[] }) {
  const [filter, setFilter] = useState<"ALL" | ComponentComparisonRow["verdict"]>("ALL");
  const [sort, setSort] = useState<keyof ComponentComparisonRow>("weightedGap");
  const verdicts = useMemo(() => Array.from(new Set(rows.map((row) => row.verdict))), [rows]);
  const visible = useMemo(() => {
    return [...rows]
      .filter((row) => filter === "ALL" || row.verdict === filter)
      .sort((a, b) => {
        const left = a[sort];
        const right = b[sort];
        if (typeof left === "number" && typeof right === "number") return right - left;
        return String(left ?? "").localeCompare(String(right ?? ""));
      });
  }, [rows, filter, sort]);
  if (!rows.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No challenger component run has been uploaded yet.</div>;
  }
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        {(["ALL", ...verdicts] as Array<"ALL" | ComponentComparisonRow["verdict"]>).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-1 text-sm ${filter === item ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setFilter(item)}
          >
            {item === "ALL" ? "All" : item.toLowerCase()}
          </button>
        ))}
        <select className="rounded border border-line bg-white px-3 py-1 text-sm" value={sort} onChange={(event) => setSort(event.target.value as keyof ComponentComparisonRow)}>
          <option value="weightedGap">Sort: weight x gap</option>
          <option value="weight">Sort: weight</option>
          <option value="productionMae">Sort: production MAE</option>
          <option value="hrnnMae">Sort: HRNN MAE</option>
          <option value="iGruMae">Sort: I-GRU MAE</option>
          <option value="seasonalArMae">Sort: seasonal AR MAE</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase text-muted">
            <tr>
              <th className="py-2 pr-4">Component</th>
              <th className="py-2 pr-4">Verdict</th>
              <th className="py-2 pr-4">Best model</th>
              <th className="py-2 pr-4">Weight</th>
              <th className="py-2 pr-4">Production</th>
              <th className="py-2 pr-4">HRNN</th>
              <th className="py-2 pr-4">I-GRU</th>
              <th className="py-2 pr-4">Seasonal AR</th>
              <th className="py-2 pr-4">Weight x gap</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => (
              <tr key={row.itemCode} className="border-b border-line/70 align-top">
                <td className="max-w-[360px] py-2 pr-4">
                  <Link href={`/components/${encodeURIComponent(row.itemCode)}`} className="font-medium text-teal hover:underline">
                    {row.name}
                  </Link>
                  <div className="text-xs text-muted">
                    <Link href={`/challenger/${row.itemCode}`} className="hover:underline">
                      {row.itemCode} challenger chart
                    </Link>
                  </div>
                </td>
                <td className="py-2 pr-4">
                  <span className={`rounded px-2 py-1 text-xs ${row.verdict === "HRNN WINS" || row.verdict === "I-GRU WINS" ? "bg-teal/10 text-teal" : row.verdict === "SEASONAL AR WINS" ? "bg-amber-50 text-amber-800" : row.verdict === "PRODUCTION WINS" ? "bg-sky/10 text-sky" : "bg-wash text-muted"}`}>
                    {row.verdict.toLowerCase()}
                  </span>
                </td>
                <td className="py-2 pr-4">{row.bestModel}</td>
                <td className="py-2 pr-4">{row.weight.toFixed(3)}</td>
                <td className="py-2 pr-4">{pp(row.productionMae)}</td>
                <td className="py-2 pr-4">{pp(row.hrnnMae)}</td>
                <td className="py-2 pr-4">{pp(row.iGruMae)}</td>
                <td className="py-2 pr-4">{pp(row.seasonalArMae)}</td>
                <td className="py-2 pr-4">{row.weightedGap.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ChallengerCurrentForecastTable({ current }: { current: ChallengerCurrentForecast | null }) {
  if (!current) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No current challenger forecast comparison has been generated yet.</div>;
  }
  const models = [
    ["actual", "Actual CPI"],
    ["production", "Production model"],
    ["productionTier1", "Tier 1 fallback"],
    ["productionTier3", "Tier 3 fallback"],
    ["hrnn", "HRNN"],
    ["iGru", "I-GRU"],
    ["seasonalAr", "Seasonal AR"]
  ] as const;
  const measures = [
    ["saMm", "SA m/m"],
    ["nsaMm", "NSA m/m"],
    ["saYoy", "SA y/y"],
    ["nsaYoy", "NSA y/y"]
  ] as const;
  return (
    <div>
      <div className="mb-3 rounded bg-wash p-3 text-sm text-muted">
        Forecast month {formatMonth(current.forecastMonth)}. Data through {formatMonth(current.dataThrough)}.
        Columns compare Actual CPI, the production model, Tier 1/Tier 3 fallback baselines, HRNN, I-GRU, and Seasonal AR. Actual CPI stays n/a until that month is present in the local BLS cache.
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase text-muted">
            <tr>
              <th className="py-2 pr-4">Series</th>
              <th className="py-2 pr-4">Measure</th>
              {models.map(([, label]) => <th key={label} className="py-2 pr-4">{label}</th>)}
            </tr>
          </thead>
          <tbody>
            {current.rows.flatMap((row) =>
              measures.map(([key, label]) => (
                <tr key={`${row.series}-${key}`} className="border-b border-line/70">
                  <td className="py-2 pr-4 font-medium">{row.label}</td>
                  <td className="py-2 pr-4 text-muted">{label}</td>
                  {models.map(([model]) => (
                    <td key={model} className="py-2 pr-4">{p3(row[model]?.[key] ?? null)}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ChallengerMajorComponentsTable({
  diagnostics,
  current
}: {
  diagnostics: ChallengerMajorComponentRow[];
  current: ChallengerCurrentForecast | null;
}) {
  const models = [
    ["production", "Legacy proxy (not full model)"],
    ["productionTier1", "Tier 1 fallback"],
    ["productionTier3", "Tier 3 fallback"],
    ["hrnn", "HRNN"],
    ["iGru", "I-GRU"],
    ["seasonalAr", "Seasonal AR"]
  ] as const;
  const currentByCode = new Map((current?.majorRows ?? []).map((row) => [row.series, row]));
  if (!diagnostics.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No major-component challenger diagnostics have been generated yet.</div>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase text-muted">
          <tr>
            <th className="py-2 pr-4">Component</th>
            <th className="py-2 pr-4">Weight</th>
            <th className="py-2 pr-4">Latest actual</th>
            {models.map(([, label]) => (
              <th key={label} className="py-2 pr-4">{label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {diagnostics.map((row) => {
            const currentRow = currentByCode.get(row.itemCode);
            return (
              <tr key={row.itemCode} className="border-b border-line/70 align-top">
                <td className="min-w-[220px] py-3 pr-4">
                  <div className="font-medium">{row.name}</div>
                  <div className="text-xs text-muted">{row.itemCode}</div>
                </td>
                <td className="py-3 pr-4">{row.weight === null || row.weight === undefined ? "n/a" : `${row.weight.toFixed(3)}%`}</td>
                <td className="py-3 pr-4">
                  <div>{formatMonth(row.latestActualMonth)}</div>
                  <div className="text-xs text-muted">SA {p3(row.latestActual.saMm)}</div>
                  <div className="text-xs text-muted">NSA {p3(row.latestActual.nsaMm)}</div>
                </td>
                {models.map(([model]) => {
                  const latestError = row.latestError[model];
                  const mae = row.windowC[model];
                  const june = currentRow?.[model]?.saMm ?? null;
                  return (
                    <td key={model} className="min-w-[150px] py-3 pr-4">
                      <div className="font-medium">Jun SA {p3(june)}</div>
                      <div className="text-xs text-muted">Latest error {p3(latestError?.saMm ?? null)}</div>
                      <div className="text-xs text-muted">Window C MAE {p3(mae?.saMmMae ?? null)}</div>
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

export function ChallengerRollingChart({
  result,
  rolling24,
  includeLegacyProxy = false
}: {
  result?: ChallengerResult;
  rolling24?: ChallengerWindow["rolling24"];
  includeLegacyProxy?: boolean;
}) {
  const sourceRows = rolling24 ?? result?.windows.C.rolling24 ?? [];
  const data = sourceRows.map((row) => ({
    month: row.month,
    ...(includeLegacyProxy ? { production: row.production === null || row.production === undefined ? null : row.production * 100 } : {}),
    productionTier1: row.productionTier1 === null || row.productionTier1 === undefined ? null : row.productionTier1 * 100,
    productionTier3: row.productionTier3 === null || row.productionTier3 === undefined ? null : row.productionTier3 * 100,
    hrnn: row.hrnn === null ? null : row.hrnn * 100,
    iGru: row.iGru === null ? null : row.iGru * 100,
    seasonalAr: row.seasonalAr === null ? null : row.seasonalAr * 100
  }));
  return (
    <div>
      <div className="mb-2 text-sm text-muted">
        Each point is MAE over the latest 24 available forecast months ending at that date; early window-C points use the shorter available history until 24 months exist.
      </div>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
            <CartesianGrid stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
            <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(2)}`} />
            <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={(value) => [`${Number(value).toFixed(2)} pp`, "Trailing 24m MAE"]} />
            <Legend />
            {includeLegacyProxy ? <Line type="monotone" dataKey="production" name="Legacy proxy (not full model)" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} /> : null}
            <Line type="monotone" dataKey="productionTier1" name="Tier 1 fallback" stroke="#0ea5e9" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="productionTier3" name="Tier 3 fallback" stroke="#dc2626" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="hrnn" name="HRNN" stroke="#0f766e" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="iGru" name="I-GRU" stroke="#7c3aed" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="seasonalAr" name="Seasonal AR" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function ChallengerComponentChart({ rows }: { rows: ChallengerSeriesRow[] }) {
  const data = rows.map((row) => ({
    month: row.month,
    actual: row.actualNsaMm === null ? null : row.actualNsaMm * 100,
    production: row.productionNsaMm === null ? null : row.productionNsaMm * 100,
    hrnn: row.hrnnNsaMm === null ? null : row.hrnnNsaMm * 100,
    iGru: row.iGruNsaMm === null ? null : row.iGruNsaMm * 100,
    seasonalAr: row.seasonalArNsaMm === null ? null : row.seasonalArNsaMm * 100
  }));
  if (!data.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No component challenger series is available for this item yet.</div>;
  }
  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
          <CartesianGrid stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
          <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(1)}%`} />
          <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={(value) => [formatPercent(Number(value) / 100), "NSA m/m"]} />
          <Legend />
          <Line type="monotone" dataKey="actual" name="Actual" stroke="#111827" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="production" name="Production" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="hrnn" name="HRNN" stroke="#0f766e" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="iGru" name="I-GRU" stroke="#7c3aed" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="seasonalAr" name="Seasonal AR" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ModelComparisonTimeline({ result }: { result: ModelComparisonResult }) {
  const [basis, setBasis] = useState<"Sa" | "Nsa">("Sa");
  const [range, setRange] = useState<"full" | "common" | "5y">("common");
  const [enabled, setEnabled] = useState<Record<ModelComparisonModelKey, boolean>>({
    productionTier1: true,
    productionTier3: true,
    hrnn: true,
    iGru: true,
    seasonalAr: true
  });
  const models = Object.entries(result.models) as Array<[ModelComparisonModelKey, { label: string; color: string }]>;
  const data = useMemo(() => {
    const cutoff = range === "common" ? result.commonStart : range === "5y" ? "2021-06" : "0000-00";
    return result.rows
      .filter((row) => row.month >= cutoff)
      .map((row) => ({
        ...row,
        actualMmPct: Number(row[`actual${basis}Mm`] ?? NaN) * 100,
        actualYoyPct: Number(row[`actual${basis}Yoy`] ?? NaN) * 100
      }));
  }, [basis, range, result]);
  const mmMeasure = `${basis}Mm` as "SaMm" | "NsaMm";
  const yoyMeasure = `${basis}Yoy` as "SaYoy" | "NsaYoy";
  const errorMeasure = `${basis}YoyErrorBp` as "SaYoyErrorBp" | "NsaYoyErrorBp";
  const pctFormatter = (value: unknown) => [`${Number(value).toFixed(3)}%`, basis === "Sa" ? "SA" : "NSA"];
  const bpFormatter = (value: unknown) => [`${Number(value).toFixed(2)} bp`, "predicted - actual"];
  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        {(["Sa", "Nsa"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-1 text-sm ${basis === item ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setBasis(item)}
          >
            {item === "Sa" ? "SA" : "NSA"} m/m
          </button>
        ))}
        {(["full", "common", "5y"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-1 text-sm ${range === item ? "border-sky bg-sky text-white" : "border-line bg-white"}`}
            onClick={() => setRange(item)}
          >
            {item === "full" ? "Full span" : item === "common" ? "2022-present" : "Last 5y"}
          </button>
        ))}
        {models.map(([key, spec]) => (
          <label key={key} className="flex items-center gap-2 rounded border border-line bg-white px-3 py-1 text-sm">
            <input
              type="checkbox"
              checked={enabled[key]}
              onChange={(event) => setEnabled((current) => ({ ...current, [key]: event.target.checked }))}
            />
            <span style={{ color: spec.color }}>{spec.label}</span>
          </label>
        ))}
      </div>
      <div className="grid gap-4">
        <div>
          <div className="mb-2 text-sm font-semibold">Headline CPI {basis === "Sa" ? "SA" : "NSA"} m/m: actual vs one-step-ahead predictions</div>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
                <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(1)}%`} />
                <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={pctFormatter} />
                <ReferenceLine y={0} stroke="#94a3b8" />
                <ReferenceArea x1="2022-01" x2="2026-12" fill="#e0f2fe" fillOpacity={0.22} />
                <Legend />
                <Line type="monotone" dataKey="actualMmPct" name={`Actual ${basis} m/m`} stroke="#111827" strokeWidth={2.6} dot={false} isAnimationActive={false} />
                {models.map(([key, spec]) => enabled[key] ? (
                  <Line key={key} type="monotone" dataKey={(row) => {
                    const value = row[modelValueKey(key, mmMeasure)];
                    return value === null || value === undefined ? null : Number(value) * 100;
                  }} name={spec.label} stroke={spec.color} strokeWidth={1.3} dot={false} isAnimationActive={false} connectNulls={false} />
                ) : null)}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-semibold">Headline CPI {basis === "Sa" ? "SA" : "NSA"} y/y: y/y = 11 actual months + 1 forecast month</div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
                <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(1)}%`} />
                <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={pctFormatter} />
                <ReferenceArea x1="2022-01" x2="2026-12" fill="#e0f2fe" fillOpacity={0.22} />
                <Legend />
                <Line type="monotone" dataKey="actualYoyPct" name={`Actual ${basis} y/y`} stroke="#111827" strokeWidth={2.6} dot={false} isAnimationActive={false} />
                {models.map(([key, spec]) => enabled[key] ? (
                  <Line key={key} type="monotone" dataKey={(row) => {
                    const value = row[modelValueKey(key, yoyMeasure)];
                    return value === null || value === undefined ? null : Number(value) * 100;
                  }} name={spec.label} stroke={spec.color} strokeWidth={1.3} dot={false} isAnimationActive={false} connectNulls={false} />
                ) : null)}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-semibold">Y/y prediction error, predicted minus actual</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
                <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(0)}`} />
                <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={bpFormatter} />
                <ReferenceLine y={0} stroke="#94a3b8" />
                <Legend />
                {models.map(([key, spec]) => enabled[key] ? (
                  <Line key={key} type="monotone" dataKey={(row) => row[modelValueKey(key, errorMeasure)]} name={spec.label} stroke={spec.color} strokeWidth={1.3} dot={false} isAnimationActive={false} connectNulls={false} />
                ) : null)}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
