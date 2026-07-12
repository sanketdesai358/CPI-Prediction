"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { ComponentTrend, TrendGroup, TrendSort } from "@/lib/component-trends";
import {
  filterComponentTrends,
  selectDisplayTrends,
  sortComponentTrends,
  TREND_GROUPS,
  trendSummary
} from "@/lib/component-trends";
import { formatIndex, formatMonth, formatWeight } from "@/lib/format";

type TimeRange = "5y" | "10y";
type ScaleMode = "independent" | "shared";

function pct(value: number | null | undefined, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${value.toFixed(digits)}%`;
}

function pp(value: number | null | undefined, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${value >= 0 ? "+" : ""}${value.toFixed(digits)} pp`;
}

function compactMonth(month: string) {
  return formatMonth(month).replace(" ", "\n");
}

function chartData(trend: ComponentTrend, range: TimeRange) {
  const limit = range === "5y" ? 60 : 120;
  return trend.points.slice(-limit).map((point) => ({
    month: point.month,
    yoy: point.yoy,
    nsaIndex: point.nsaIndex,
    weight: point.weight
  }));
}

function domainFor(values: Array<number | null>, includeTwoLine: boolean): [number, number] {
  const clean = values.filter((value): value is number => typeof value === "number" && Number.isFinite(value));
  if (includeTwoLine) clean.push(2);
  clean.push(0);
  if (!clean.length) return [-1, 1];
  const min = Math.min(...clean);
  const max = Math.max(...clean);
  const spread = Math.max(max - min, 1);
  return [Math.floor((min - spread * 0.12) * 10) / 10, Math.ceil((max + spread * 0.12) * 10) / 10];
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ payload: Record<string, unknown> }>; label?: string }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded border border-line bg-white p-2 text-xs shadow-subtle">
      <div className="font-semibold text-ink">{formatMonth(String(label))}</div>
      <div>NSA index: {formatIndex(row.nsaIndex as number | null)}</div>
      <div>YoY: {pct(row.yoy as number | null, 2)}</div>
      <div>Weight: {formatWeight(row.weight as number | null)}</div>
    </div>
  );
}

function SummaryCard({ label, trend }: { label: string; trend: ComponentTrend | null }) {
  return (
    <div className="rounded border border-line bg-white p-4 shadow-subtle">
      <div className="text-xs font-medium uppercase tracking-wide text-muted">{label}</div>
      {trend ? (
        <>
          <div className="mt-2 text-base font-semibold">{trend.displayName}</div>
          <div className="mt-1 text-2xl font-semibold">{pct(trend.latestYoy)}</div>
          <div className="mt-1 text-xs text-muted">
            3m {pp(trend.threeMonthChange)} - weight {formatWeight(trend.currentRi)}
          </div>
        </>
      ) : (
        <div className="mt-2 text-sm text-muted">No matching component</div>
      )}
    </div>
  );
}

function TrendCard({
  trend,
  range,
  showTwoLine,
  scaleMode,
  sharedDomain,
  onOpen
}: {
  trend: ComponentTrend;
  range: TimeRange;
  showTwoLine: boolean;
  scaleMode: ScaleMode;
  sharedDomain: [number, number];
  onOpen: (trend: ComponentTrend) => void;
}) {
  const data = chartData(trend, range);
  const domain = scaleMode === "shared" ? sharedDomain : domainFor(data.map((point) => point.yoy), showTwoLine);
  const shortCoverage = trend.coverageMonths < (range === "5y" ? 60 : 120);
  return (
    <button
      type="button"
      onClick={() => onOpen(trend)}
      className="focus-ring rounded border border-line bg-white p-4 text-left shadow-subtle transition hover:border-teal"
      aria-label={`Open expanded chart for ${trend.displayName}`}
    >
      <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-base font-semibold">{trend.displayName}</div>
          <div className="mt-1 text-xs text-muted">
            {trend.seriesId} - {trend.latestMonth ? formatMonth(trend.latestMonth) : "No latest month"}
          </div>
        </div>
        <span className="rounded border border-line bg-wash px-2 py-1 text-xs text-muted">{trend.group}</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
        <div>
          <div className="text-muted">Weight</div>
          <div className="font-semibold">{formatWeight(trend.currentRi)}</div>
        </div>
        <div>
          <div className="text-muted">Latest YoY</div>
          <div className="font-semibold">{pct(trend.latestYoy)}</div>
        </div>
        <div>
          <div className="text-muted">3m change</div>
          <div className="font-semibold">{pp(trend.threeMonthChange)}</div>
        </div>
      </div>
      {shortCoverage ? (
        <div className="mb-2 rounded border border-amber/30 bg-amber/5 px-2 py-1 text-xs text-amber">
          Partial coverage: {trend.coverageMonths} YoY months
        </div>
      ) : null}
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 0, right: 8, top: 6, bottom: 0 }}>
            <CartesianGrid stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
            <YAxis
              domain={domain}
              width={48}
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => `${Number(value).toFixed(1)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#64748b" />
            {showTwoLine ? <ReferenceLine y={2} stroke="#b45309" strokeDasharray="4 4" label={{ value: "2%", fontSize: 10 }} /> : null}
            <Line type="monotone" dataKey="yoy" stroke="#0f766e" strokeWidth={2} dot={false} isAnimationActive={false} connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {scaleMode === "independent" ? (
        <div className="mt-1 text-xs text-muted">
          Independent scale: {pct(domain[0])} to {pct(domain[1])}
        </div>
      ) : null}
    </button>
  );
}

function DetailModal({ trend, onClose, showTwoLine }: { trend: ComponentTrend; onClose: () => void; showTwoLine: boolean }) {
  const yoyData = chartData(trend, "10y");
  const indexData = trend.indexPoints;
  const yoyDomain = domainFor(yoyData.map((point) => point.yoy), showTwoLine);
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-ink/40 p-4" role="dialog" aria-modal="true" aria-label={`${trend.displayName} detail`}>
      <div className="mx-auto max-w-5xl rounded border border-line bg-white p-4 shadow-subtle">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-teal">{trend.group}</div>
            <h2 className="text-xl font-semibold">{trend.displayName}</h2>
            <div className="mt-1 text-sm text-muted">
              {trend.officialName} - {trend.seriesId}
            </div>
          </div>
          <button type="button" className="focus-ring rounded border border-line px-3 py-1 text-sm hover:border-teal" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="grid gap-3 text-sm md:grid-cols-4">
          <div className="rounded border border-line bg-wash p-3">
            <div className="text-xs uppercase text-muted">Latest YoY</div>
            <div className="text-xl font-semibold">{pct(trend.latestYoy)}</div>
          </div>
          <div className="rounded border border-line bg-wash p-3">
            <div className="text-xs uppercase text-muted">Previous month YoY</div>
            <div className="text-xl font-semibold">{pct(trend.previousMonthYoy)}</div>
          </div>
          <div className="rounded border border-line bg-wash p-3">
            <div className="text-xs uppercase text-muted">3m change</div>
            <div className="text-xl font-semibold">{pp(trend.threeMonthChange)}</div>
          </div>
          <div className="rounded border border-line bg-wash p-3">
            <div className="text-xs uppercase text-muted">12m change</div>
            <div className="text-xl font-semibold">{pp(trend.twelveMonthChange)}</div>
          </div>
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <h3 className="mb-2 text-sm font-semibold">10-year YoY inflation</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={yoyData} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
                  <CartesianGrid stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
                  <YAxis domain={yoyDomain} tickFormatter={(value) => `${Number(value).toFixed(1)}%`} width={52} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={0} stroke="#64748b" />
                  {showTwoLine ? <ReferenceLine y={2} stroke="#b45309" strokeDasharray="4 4" /> : null}
                  <Line type="monotone" dataKey="yoy" stroke="#0f766e" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div>
            <h3 className="mb-2 text-sm font-semibold">NSA index level</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={indexData} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
                  <CartesianGrid stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="month" tickFormatter={compactMonth} minTickGap={24} tick={{ fontSize: 11 }} />
                  <YAxis width={52} />
                  <Tooltip labelFormatter={(label) => formatMonth(String(label))} formatter={(value) => [formatIndex(Number(value)), "NSA index"]} />
                  <Line type="monotone" dataKey="nsaIndex" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        <div className="mt-4 grid gap-3 text-sm md:grid-cols-3">
          <div>Current CPI weight: <strong>{formatWeight(trend.currentRi)}</strong></div>
          <div>
            10y minimum: <strong>{trend.tenYearMin ? `${pct(trend.tenYearMin.value)} (${formatMonth(trend.tenYearMin.month)})` : "n/a"}</strong>
          </div>
          <div>
            10y maximum: <strong>{trend.tenYearMax ? `${pct(trend.tenYearMax.value)} (${formatMonth(trend.tenYearMax.month)})` : "n/a"}</strong>
          </div>
          <div>10y average YoY: <strong>{pct(trend.tenYearAverage)}</strong></div>
          <div>Latest reference month: <strong>{trend.latestMonth ? formatMonth(trend.latestMonth) : "n/a"}</strong></div>
          <div>Source: <strong>BLS CPI-U, U.S. city average, NSA index</strong></div>
        </div>
      </div>
    </div>
  );
}

export function ComponentTrendsDashboard({ trends }: { trends: ComponentTrend[] }) {
  const [search, setSearch] = useState("");
  const [group, setGroup] = useState<TrendGroup | "All">("All");
  const [sort, setSort] = useState<TrendSort>("weightDesc");
  const [displayCount, setDisplayCount] = useState<10 | 15 | 20>(20);
  const [range, setRange] = useState<TimeRange>("10y");
  const [showTwoLine, setShowTwoLine] = useState(true);
  const [scaleMode, setScaleMode] = useState<ScaleMode>("independent");
  const [selected, setSelected] = useState<ComponentTrend | null>(null);

  const filtered = useMemo(() => filterComponentTrends(trends, { search, group }), [trends, search, group]);
  const sorted = useMemo(() => sortComponentTrends(filtered, sort), [filtered, sort]);
  const visible = useMemo(() => selectDisplayTrends(sorted, displayCount), [sorted, displayCount]);
  const summary = useMemo(() => trendSummary(filtered), [filtered]);
  const sharedDomain = useMemo(() => {
    const values = visible.flatMap((trend) => chartData(trend, range).map((point) => point.yoy));
    return domainFor(values, showTwoLine);
  }, [visible, range, showTwoLine]);

  return (
    <div>
      <div className="rounded border border-line bg-white p-4 shadow-subtle">
        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          <label className="text-sm">
            <span className="mb-1 block font-medium">Search</span>
            <input
              className="focus-ring w-full rounded border border-line bg-white px-3 py-2"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Component name"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium">Category</span>
            <select className="focus-ring w-full rounded border border-line bg-white px-3 py-2" value={group} onChange={(event) => setGroup(event.target.value as TrendGroup | "All")}>
              <option value="All">All categories</option>
              {TREND_GROUPS.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium">Sort</span>
            <select className="focus-ring w-full rounded border border-line bg-white px-3 py-2" value={sort} onChange={(event) => setSort(event.target.value as TrendSort)}>
              <option value="weightDesc">CPI weight, descending</option>
              <option value="latestDesc">Latest YoY, descending</option>
              <option value="latestAsc">Latest YoY, ascending</option>
              <option value="accelerationDesc">Three-month acceleration</option>
              <option value="accelerationAsc">Three-month deceleration</option>
              <option value="alpha">Alphabetical</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium">Display</span>
            <select className="focus-ring w-full rounded border border-line bg-white px-3 py-2" value={displayCount} onChange={(event) => setDisplayCount(Number(event.target.value) as 10 | 15 | 20)}>
              <option value={10}>10 charts</option>
              <option value={15}>15 charts</option>
              <option value={20}>20 charts</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium">Time range</span>
            <select className="focus-ring w-full rounded border border-line bg-white px-3 py-2" value={range} onChange={(event) => setRange(event.target.value as TimeRange)}>
              <option value="5y">5 years</option>
              <option value="10y">10 years</option>
            </select>
          </label>
          <label className="flex items-end gap-2 text-sm">
            <input
              type="checkbox"
              className="mb-3 h-4 w-4"
              checked={showTwoLine}
              onChange={(event) => setShowTwoLine(event.target.checked)}
            />
            <span className="pb-2">Show 2% line</span>
          </label>
        </div>
        <fieldset className="mt-3 flex flex-wrap gap-2 text-sm">
          <legend className="sr-only">Y-axis scale mode</legend>
          <button
            type="button"
            className={`focus-ring rounded border px-3 py-1.5 ${scaleMode === "independent" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setScaleMode("independent")}
          >
            Independent scales
          </button>
          <button
            type="button"
            className={`focus-ring rounded border px-3 py-1.5 ${scaleMode === "shared" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}
            onClick={() => setScaleMode("shared")}
          >
            Shared scale
          </button>
        </fieldset>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Highest latest YoY inflation" trend={summary.highest} />
        <SummaryCard label="Lowest latest YoY inflation" trend={summary.lowest} />
        <SummaryCard label="Largest three-month acceleration" trend={summary.acceleration} />
        <SummaryCard label="Largest three-month deceleration" trend={summary.deceleration} />
      </div>

      {visible.length ? (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {visible.map((trend) => (
            <TrendCard
              key={trend.itemCode}
              trend={trend}
              range={range}
              showTwoLine={showTwoLine}
              scaleMode={scaleMode}
              sharedDomain={sharedDomain}
              onOpen={setSelected}
            />
          ))}
        </div>
      ) : (
        <div className="mt-4 rounded border border-line bg-white p-6 text-sm text-muted shadow-subtle">
          No components match the current filters.
        </div>
      )}

      {selected ? <DetailModal trend={selected} onClose={() => setSelected(null)} showTwoLine={showTwoLine} /> : null}
    </div>
  );
}
