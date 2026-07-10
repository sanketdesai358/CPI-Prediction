"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { BacktestResult, ComponentEntry, ContributionRow, ForecastRun, ScoreRow, SeriesPoint } from "@/lib/types";
import { formatMonth, formatPercent, formatPp, formatWeight } from "@/lib/format";

type TinyPoint = { month: string; value: number | null };

function compactMonth(month: string) {
  return formatMonth(month).replace(" ", "\n");
}

function compactProjectionMonth(month: string) {
  return `${formatMonth(month).split(" ")[0]} proj`;
}

function colorFor(value: number | null | undefined) {
  if (value === null || value === undefined) return "#94a3b8";
  if (value > 0.01) return "#dc2626";
  if (value > 0) return "#f59e0b";
  if (value < -0.005) return "#0f766e";
  return "#2563eb";
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function hexToRgb(hex: string) {
  const normalized = hex.replace("#", "");
  return {
    r: parseInt(normalized.slice(0, 2), 16),
    g: parseInt(normalized.slice(2, 4), 16),
    b: parseInt(normalized.slice(4, 6), 16)
  };
}

function mixColor(from: string, to: string, amount: number) {
  const a = hexToRgb(from);
  const b = hexToRgb(to);
  const mix = (start: number, end: number) => Math.round(start + (end - start) * amount);
  return `rgb(${mix(a.r, b.r)}, ${mix(a.g, b.g)}, ${mix(a.b, b.b)})`;
}

type HeatmapStop = { value: number; color: string };

const HEATMAP_MOMENTUM_STOPS: HeatmapStop[] = [
  { value: -0.02, color: "#0f766e" },
  { value: -0.01, color: "#2563eb" },
  { value: 0, color: "#f8fafc" },
  { value: 0.005, color: "#f59e0b" },
  { value: 0.01, color: "#dc2626" },
  { value: 0.02, color: "#7f1d1d" }
];

const HEATMAP_CONTRIBUTION_STOPS: HeatmapStop[] = [
  { value: -0.2, color: "#0f766e" },
  { value: -0.1, color: "#2563eb" },
  { value: 0, color: "#f8fafc" },
  { value: 0.05, color: "#f59e0b" },
  { value: 0.1, color: "#dc2626" },
  { value: 0.2, color: "#7f1d1d" }
];

function heatmapColorFor(value: number | null | undefined, stops: HeatmapStop[]) {
  if (value === null || value === undefined) return "#cbd5e1";
  const bounded = clamp(value, stops[0].value, stops[stops.length - 1].value);
  for (let index = 1; index < stops.length; index += 1) {
    const left = stops[index - 1];
    const right = stops[index];
    if (bounded <= right.value) {
      const amount = (bounded - left.value) / (right.value - left.value);
      return mixColor(left.color, right.color, amount);
    }
  }
  return stops[stops.length - 1].color;
}

function heatmapTextClass(value: number | null | undefined, neutralThreshold: number) {
  if (value === null || value === undefined) return "text-slate-600";
  return Math.abs(value) < neutralThreshold ? "text-slate-800" : "text-white";
}

function formatHeatmapValue(value: number | null | undefined) {
  if (value === null || value === undefined) return "n/a";
  const percent = value * 100;
  if (Math.abs(percent) >= 10) return `${percent.toFixed(0)}%`;
  return `${percent.toFixed(1)}%`;
}

function formatContributionValue(value: number | null | undefined) {
  if (value === null || value === undefined) return "n/a";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function formatContributionStd(value: number | null | undefined) {
  if (value === null || value === undefined) return "n/a";
  return value.toFixed(2);
}

function standardDeviation(values: Array<number | null | undefined>) {
  const clean = values.filter((value): value is number => value !== null && value !== undefined && Number.isFinite(value));
  if (clean.length < 2) return null;
  const mean = clean.reduce((sum, value) => sum + value, 0) / clean.length;
  const variance = clean.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (clean.length - 1);
  return Math.sqrt(variance);
}

export function Sparkline({ points }: { points: TinyPoint[] }) {
  return (
    <div className="h-16">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points}>
          <Area dataKey="value" stroke="#0f766e" fill="#ccfbf1" strokeWidth={2} dot={false} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ContributionWaterfall({ rows }: { rows: ContributionRow[] }) {
  const data = rows.slice(0, 12).map((row) => ({
    name: row.itemCode,
    label: row.name,
    contribution: row.contribution ?? 0,
    fill: colorFor(row.contribution)
  }));
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 40 }}>
          <CartesianGrid stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="name" angle={-35} textAnchor="end" interval={0} height={60} tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(value) => `${Number(value).toFixed(2)}`} width={42} />
          <Tooltip
            formatter={(value) => [formatPp(Number(value)), "Contribution"]}
            labelFormatter={(_, payload) => payload?.[0]?.payload?.label ?? ""}
          />
          <ReferenceLine y={0} stroke="#64748b" />
          <Bar dataKey="contribution" fill="#2563eb" isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ComponentExplorer({ entries }: { entries: ComponentEntry[] }) {
  const rows = useMemo(() => entries.filter((entry) => (entry.currentRi ?? 0) > 0).slice(0, 160), [entries]);
  return (
    <div>
      <div className="mb-3 text-sm text-muted">Seasonally adjusted m/m movement by component.</div>
      <div className="flex flex-wrap gap-2">
        {rows.map((entry) => {
          const value = entry.latest.saMm;
          const basis = Math.max(70, Math.min(260, (entry.currentRi ?? 0) * 12));
          return (
            <a
              key={entry.itemCode}
              href={`/components/${entry.itemCode}`}
              className="min-h-24 rounded border border-line p-3 text-white shadow-subtle"
              style={{ flex: `${basis} 1 ${basis}px`, backgroundColor: colorFor(value) }}
              title={`${entry.name}: ${formatPercent(entry.latest.saMm)}`}
            >
              <div className="text-sm font-semibold">{entry.name}</div>
              <div className="mt-1 text-xs opacity-90">
                {entry.itemCode} · {formatWeight(entry.currentRi)}
              </div>
              <div className="mt-3 text-lg font-semibold">
                {formatPercent(entry.latest.saMm)}
              </div>
              <div className="text-xs opacity-90">seasonally adjusted m/m</div>
            </a>
          );
        })}
      </div>
    </div>
  );
}

export function DetailChart({ history }: { history: SeriesPoint[] }) {
  const [range, setRange] = useState<"1y" | "5y" | "max">("5y");
  const [mode, setMode] = useState<"level" | "mm">("mm");
  const data = useMemo(() => {
    const slice = range === "1y" ? history.slice(-12) : range === "5y" ? history.slice(-60) : history;
    return slice.map((point) => ({
      month: point.month,
      level: point.saIndex,
      mm: point.saMm === null ? null : point.saMm * 100
    }));
  }, [history, range]);
  const key = mode === "level" ? "level" : mode;
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        {(["level", "mm"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-1 text-sm ${mode === item ? "border-teal bg-teal text-white" : "border-line"}`}
            onClick={() => setMode(item)}
          >
            {item === "level" ? "SA level" : "SA m/m"}
          </button>
        ))}
        {(["1y", "5y", "max"] as const).map((item) => (
          <button
            key={item}
            className={`rounded border px-3 py-1 text-sm ${range === item ? "border-sky bg-sky text-white" : "border-line"}`}
            onClick={() => setRange(item)}
          >
            {item}
          </button>
        ))}
      </div>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
            <CartesianGrid stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
            <YAxis width={52} />
            <Tooltip labelFormatter={(label) => formatMonth(String(label))} />
            <ReferenceLine y={0} stroke="#94a3b8" />
            <Line type="monotone" dataKey={key} stroke="#0f766e" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function HeatmapGrid({ entries, months, forecast }: { entries: ComponentEntry[]; months: string[]; forecast?: ForecastRun | null }) {
  const [mode, setMode] = useState<"momentum" | "contribution">("momentum");
  const [sortState, setSortState] = useState<{ key: "ri" | "std" | string; direction: "desc" | "asc" }>({
    key: "ri",
    direction: "desc"
  });
  const projectionKey = forecast?.forecastMonth && !months.includes(forecast.forecastMonth) ? `${forecast.forecastMonth}-projection` : null;
  const columns = useMemo(
    () => [
      ...months.map((month) => ({ key: month, month, label: month.slice(5), isProjection: false })),
      ...(projectionKey && forecast
        ? [{ key: projectionKey, month: forecast.forecastMonth, label: compactProjectionMonth(forecast.forecastMonth), isProjection: true }]
        : [])
    ],
    [forecast, months, projectionKey]
  );
  const forecastByItem = useMemo(
    () => new Map((forecast?.projectionComponents ?? forecast?.components ?? []).map((component) => [component.itemCode, component])),
    [forecast]
  );
  const config = mode === "momentum"
    ? {
        title: "SA m/m color scale",
        note: "Official BLS SA where available; otherwise a derived seasonal proxy from the NSA index. Cool colors are negative prints; warm colors are positive prints.",
        stops: HEATMAP_MOMENTUM_STOPS,
        labels: ["-2.0%", "-1.0%", "0.0%", "+1.0%", "+2.0%+"],
        neutralThreshold: 0.0015,
        formatCell: formatHeatmapValue,
        titleSuffix: (value: number | null | undefined) => formatPercent(value)
      }
    : {
        title: "Headline contribution color scale",
        note: "Cells show percentage-point contribution to the monthly CPI print: RI weight x SA m/m or derived SA proxy.",
        stops: HEATMAP_CONTRIBUTION_STOPS,
        labels: ["-0.20 pp", "-0.10 pp", "0.00 pp", "+0.10 pp", "+0.20 pp+"],
        neutralThreshold: 0.015,
        formatCell: formatContributionValue,
        titleSuffix: (value: number | null | undefined) => formatPp(value)
      };
  const valueForPoint = (entry: ComponentEntry, point: SeriesPoint | undefined) => {
    if (!point || point.saMm === null || point.saMm === undefined) return null;
    return mode === "momentum" ? point.saMm : (point.ri ?? entry.currentRi ?? 0) * point.saMm;
  };
  const valueForProjection = (entry: ComponentEntry) => {
    const projected = forecastByItem.get(entry.itemCode);
    if (!projected) return null;
    return mode === "momentum" ? projected.forecast_sa_mm : projected.contribution_pp;
  };
  const projectionSource = (entry: ComponentEntry) => {
    const projected = forecastByItem.get(entry.itemCode);
    const hasProjectionMetadata = projected && "projectionSource" in projected;
    return {
      label: hasProjectionMetadata
        ? projected.projectionSource === "AR fallback"
          ? "AR"
          : projected.projectionSource === "aggregate"
            ? "agg"
            : projected.projectionSource
        : "model",
      detail: hasProjectionMetadata ? projected.projectionSourceDetail : "model projection",
      display: hasProjectionMetadata ? projected.displayInHeatmap !== false : true
    };
  };
  const selectSort = (key: "ri" | "std" | string) => {
    setSortState((current) => ({
      key,
      direction: current.key === key && current.direction === "desc" ? "asc" : "desc"
    }));
  };
  const sortMark = (key: "ri" | "std" | string) => {
    if (sortState.key !== key) return "";
    return sortState.direction === "desc" ? " ↓" : " ↑";
  };
  const rows = useMemo(() => {
    return entries
      .filter((entry) => entry.history.some((point) => months.includes(point.month)))
      .filter((entry) => !projectionKey || projectionSource(entry).display)
      .map((entry) => {
        const history120 = entry.history.slice(-120).map((point) => valueForPoint(entry, point));
        const valuesByKey = new Map(entry.history.map((point) => [point.month, valueForPoint(entry, point)]));
        if (projectionKey) valuesByKey.set(projectionKey, valueForProjection(entry));
        return {
          entry,
          valuesByKey,
          tenYearStd: standardDeviation(history120),
          ri: entry.currentRi ?? null
        };
      })
      .sort((a, b) => {
        const valueForSort = (row: typeof a) => {
          if (sortState.key === "ri") return row.ri;
          if (sortState.key === "std") return row.tenYearStd;
          return row.valuesByKey.get(sortState.key) ?? null;
        };
        const left = valueForSort(a);
        const right = valueForSort(b);
        if (left === null && right === null) return (b.entry.currentRi ?? 0) - (a.entry.currentRi ?? 0);
        if (left === null) return 1;
        if (right === null) return -1;
        return sortState.direction === "desc" ? right - left : left - right;
      })
      .slice(0, 80);
  }, [entries, mode, months, projectionKey, sortState, forecastByItem]);
  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        <div className="flex flex-wrap gap-2">
          <button
            className={`rounded border px-3 py-1 text-sm ${mode === "momentum" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setMode("momentum")}
          >
            SA m/m
          </button>
          <button
            className={`rounded border px-3 py-1 text-sm ${mode === "contribution" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setMode("contribution")}
          >
            Contribution to CPI
          </button>
        </div>
      </div>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-ink">{config.title}</div>
          <div className="text-xs text-muted">{config.note}</div>
        </div>
        <div className="min-w-[320px] flex-1 sm:max-w-xl">
          <div
            className="h-3 rounded"
            style={{
              background:
                "linear-gradient(90deg, #0f766e 0%, #2563eb 25%, #f8fafc 50%, #f59e0b 62.5%, #dc2626 75%, #7f1d1d 100%)"
            }}
          />
          <div className="mt-1 grid grid-cols-5 text-[10px] text-muted">
            <span>{config.labels[0]}</span>
            <span className="text-center">{config.labels[1]}</span>
            <span className="text-center">{config.labels[2]}</span>
            <span className="text-center">{config.labels[3]}</span>
            <span className="text-right">{config.labels[4]}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted">
          <span className="h-3 w-6 rounded bg-slate-300" />
          no SA value
        </div>
      </div>
      <div className="overflow-x-auto">
      <div className="min-w-[1390px]">
        <div className="grid gap-px" style={{ gridTemplateColumns: `260px 72px 72px repeat(${columns.length}, minmax(44px, 1fr))` }}>
          <div className="sticky left-0 z-20 bg-white" />
          <button
            className="sticky left-[260px] z-20 bg-white px-2 text-center text-[10px] font-semibold uppercase text-muted hover:text-teal"
            title="Current price-updated relative importance. Click to sort."
            onClick={() => selectSort("ri")}
          >
            RI{sortMark("ri")}
          </button>
          <button
            className="sticky left-[332px] z-20 bg-white px-2 text-center text-[10px] font-semibold uppercase text-muted hover:text-teal"
            title="Standard deviation of the active heatmap values over the trailing 10 years. Click to sort."
            onClick={() => selectSort("std")}
          >
            10y sd{sortMark("std")}
          </button>
          {columns.map((column) => (
            <button
              key={column.key}
              className={`text-center text-[10px] hover:text-teal ${column.isProjection ? "font-semibold text-teal" : "text-muted"}`}
              title={`Sort by ${formatMonth(column.month)}${column.isProjection ? " projection" : ""}`}
              onClick={() => selectSort(column.key)}
            >
              {column.label}{sortMark(column.key)}
            </button>
          ))}
          {rows.map(({ entry, tenYearStd, ri }) => {
            const byMonth = new Map(entry.history.map((point) => [point.month, point]));
            return (
              <div key={entry.itemCode} className="contents">
                <a
                  href={`/components/${entry.itemCode}`}
                  className="sticky left-0 z-10 truncate bg-white px-2 py-1 text-xs shadow-[6px_0_8px_-8px_rgba(15,23,42,0.45)] hover:text-teal"
                  title={entry.name}
                >
                  {entry.name}
                </a>
                <div
                  className="sticky left-[260px] z-10 flex h-8 items-center justify-center bg-white px-2 text-[10px] font-semibold tabular-nums text-ink"
                  title={`${entry.name} current relative importance: ${formatWeight(ri)}`}
                >
                  {formatWeight(ri)}
                </div>
                <div
                  className="sticky left-[332px] z-10 flex h-8 items-center justify-center bg-white px-2 text-[10px] font-semibold tabular-nums text-ink shadow-[6px_0_8px_-8px_rgba(15,23,42,0.35)]"
                  title={`${entry.name} trailing 10-year standard deviation: ${mode === "momentum" ? formatHeatmapValue(tenYearStd) : formatContributionStd(tenYearStd)}`}
                >
                  {mode === "momentum" ? formatHeatmapValue(tenYearStd) : formatContributionStd(tenYearStd)}
                </div>
                {columns.map((column) => {
                  const point = byMonth.get(column.month);
                  const value = column.isProjection ? valueForProjection(entry) : valueForPoint(entry, point);
                  const source = column.isProjection
                    ? projectionSource(entry).detail
                    : point?.saMethod === "derived_nsa_seasonal_proxy"
                      ? "derived SA proxy from NSA index"
                      : "official BLS SA";
                  const badge = column.isProjection ? projectionSource(entry).label : null;
                  return (
                    <div
                      key={`${entry.itemCode}-${column.key}`}
                      className={`flex h-8 flex-col items-center justify-center px-1 text-[10px] font-semibold tabular-nums ${column.isProjection ? "ring-1 ring-inset ring-teal/40" : ""} ${heatmapTextClass(value, config.neutralThreshold)}`}
                      title={`${entry.name} ${formatMonth(column.month)}${column.isProjection ? " projection" : ""} ${config.titleSuffix(value)} (${source})`}
                      style={{ backgroundColor: heatmapColorFor(value, config.stops) }}
                    >
                      <span>{config.formatCell(value)}</span>
                      {badge ? <span className="mt-0.5 rounded bg-white/70 px-1 text-[8px] uppercase leading-3 text-slate-700">{badge}</span> : null}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
      </div>
    </div>
  );
}

export function ContributionExplorer({
  entries,
  months,
  headlineByMonth
}: {
  entries: ComponentEntry[];
  months: string[];
  headlineByMonth: Record<string, number | null>;
}) {
  const [month, setMonth] = useState(months[months.length - 1]);
  const [level, setLevel] = useState<"groups" | "strata">("groups");
  const rows = useMemo(() => {
    return entries
      .filter((entry) => (level === "groups" ? entry.parent === "SA0" : entry.formula !== "aggregate"))
      .map((entry) => {
        const point = entry.history.find((item) => item.month === month);
        return {
          itemCode: entry.itemCode,
          name: entry.name,
          contribution: point?.contribution ?? null,
          currentRi: point?.ri ?? entry.currentRi,
          saMm: point?.saMm ?? null
        };
      })
      .filter((row) => row.contribution !== null)
      .sort((a, b) => Math.abs(b.contribution ?? 0) - Math.abs(a.contribution ?? 0))
      .slice(0, level === "groups" ? 12 : 25);
  }, [entries, level, month]);
  const sum = rows.reduce((acc, row) => acc + (row.contribution ?? 0), 0);
  const headline = headlineByMonth[month];
  const residual = headline === null || headline === undefined ? null : headline * 100 - sum;
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        <select className="rounded border border-line bg-white px-3 py-1 text-sm" value={month} onChange={(event) => setMonth(event.target.value)}>
          {months.map((item) => (
            <option key={item} value={item}>
              {formatMonth(item)}
            </option>
          ))}
        </select>
        <button className={`rounded border px-3 py-1 text-sm ${level === "groups" ? "border-teal bg-teal text-white" : "border-line"}`} onClick={() => setLevel("groups")}>
          Groups
        </button>
        <button className={`rounded border px-3 py-1 text-sm ${level === "strata" ? "border-teal bg-teal text-white" : "border-line"}`} onClick={() => setLevel("strata")}>
          Strata
        </button>
      </div>
      <ContributionWaterfall rows={rows} />
      <div className="mt-2 text-sm text-muted">
        Visible sum {formatPp(sum)} · headline {formatPercent(headline)} · residual {formatPp(residual)}
      </div>
    </div>
  );
}

export function BacktestRollingChart({ result }: { result: BacktestResult }) {
  const data = result.rolling24.map((point) => ({
    month: point.month,
    mae: point.mae24 === null ? null : point.mae24 * 100
  }));
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
          <CartesianGrid stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
          <YAxis width={52} tickFormatter={(value) => `${Number(value).toFixed(2)}`} />
          <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={(value) => [`${Number(value).toFixed(2)} pp`, "24m MAE"]} />
          <Line type="monotone" dataKey="mae" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ScoreWaterfall({ rows }: { rows: ScoreRow[] }) {
  const mapped = rows
    .filter((row) => row.missPp !== null || row.forecastContribution !== null)
    .slice(0, 15)
    .map((row) => ({
      itemCode: row.itemCode,
      name: row.name,
      contribution: row.missPp ?? row.forecastContribution ?? 0,
      currentRi: null,
      saMm: null
    }));
  if (!mapped.length) {
    return <div className="rounded border border-line bg-wash p-4 text-sm text-muted">No score attribution yet. This appears after the BLS release is scored.</div>;
  }
  return <ContributionWaterfall rows={mapped} />;
}
