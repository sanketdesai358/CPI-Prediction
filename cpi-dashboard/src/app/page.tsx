import { ContributionWaterfall, Sparkline } from "@/components/Charts";
import { LatestRowsTable } from "@/components/DataTable";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, getForecast, sortByWeight } from "@/lib/data";
import { formatIndex, formatMonth, formatPercent, formatWeight } from "@/lib/format";

function latestSaYoy(entry: { latest: { month: string; saIndex: number | null }; history: Array<{ month: string; saIndex: number | null }> } | undefined) {
  if (!entry?.latest.saIndex) return null;
  const [year, month] = entry.latest.month.split("-").map(Number);
  const yearAgo = `${year - 1}-${String(month).padStart(2, "0")}`;
  const base = entry.history.find((point) => point.month === yearAgo)?.saIndex;
  if (!base) return null;
  return entry.latest.saIndex / base - 1;
}

export default function OverviewPage() {
  const data = getDashboardData();
  const byCode = new Map(data.entries.map((entry) => [entry.itemCode, entry]));
  const forecast = getForecast();
  const headline = byCode.get("SA0");
  const core = byCode.get("SA0L1E");
  const groups = ["SAF1", "SA0E", "SAH1", "SAT", "SAM", "SAR"].map((code) => byCode.get(code)).filter(Boolean);
  const latestRows = sortByWeight(data.entries.filter((entry) => ["SA0", "SA0L1E", "SAF1", "SA0E", "SAH1", "SAT", "SAM"].includes(entry.itemCode)));
  const countdownDate = new Date(`${data.nextRelease.releaseDate}T12:30:00Z`);
  const days = Math.max(0, Math.ceil((countdownDate.valueOf() - Date.now()) / 86_400_000));
  const headlineSaYoy = latestSaYoy(headline);
  const coreSaYoy = latestSaYoy(core);

  return (
    <>
      <PageTitle eyebrow="Overview" title="Headline, core, weights, and contribution pressure">
        Latest published reference month is {formatMonth(data.refMonth)}. All calculations are sourced from BLS
        CPI-U U.S. city average series and the current relative-importance vintage.
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard label="Headline SA m/m" value={formatPercent(data.headline.saMm)} subvalue={`SA index ${formatIndex(data.headline.saIndex)}`} tone="up" />
        <MetricCard label="Headline y/y" value={formatPercent(data.headline.nsaYoy)} subvalue={`NSA; SA ${formatPercent(headlineSaYoy)}`} tone="up" />
        <MetricCard label="Core SA m/m" value={formatPercent(data.core.saMm)} subvalue={`Core weight ${formatWeight(core?.currentRi)}`} />
        <MetricCard label="Core y/y" value={formatPercent(data.core.nsaYoy)} subvalue={`NSA; SA ${formatPercent(coreSaYoy)}`} />
      </div>
      <div className="mt-3 grid gap-3 md:grid-cols-4">
        <MetricCard label="Headline SA index" value={formatIndex(data.headline.saIndex)} subvalue={formatMonth(data.refMonth)} tone="up" />
        <MetricCard label="Next release" value={`${days} days`} subvalue={`${data.nextRelease.releaseDate} ${data.nextRelease.releaseTime}`} />
      </div>

      {forecast ? (
        <div className="mt-4">
          <Panel title={`Latest model forecast: ${formatMonth(forecast.forecastMonth)}`}>
            <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-center">
              <div>
                <div className="text-sm text-muted">Headline SA m/m P50</div>
                <div className="text-2xl font-semibold">{formatPercent(forecast.headline.saMm)}</div>
                <div className="text-xs text-muted">
                  P10 {formatPercent(forecast.headline.saInterval.p10)} / P90 {formatPercent(forecast.headline.saInterval.p90)}
                </div>
                <div className="mt-1 text-xs text-muted">
                  y/y: SA {formatPercent(forecast.headline.saYoy)} / NSA {formatPercent(forecast.headline.nsaYoy)}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted">Core SA m/m P50</div>
                <div className="text-2xl font-semibold">{formatPercent(forecast.core.saMm)}</div>
                <div className="text-xs text-muted">
                  y/y: SA {formatPercent(forecast.core.saYoy)} / NSA {formatPercent(forecast.core.nsaYoy)}
                </div>
                <div className="mt-1 text-xs text-muted">Model output, not BLS data</div>
              </div>
              <a href="/forecast" className="rounded bg-teal px-4 py-2 text-center text-sm font-medium text-white">
                Open forecast
              </a>
            </div>
          </Panel>
        </div>
      ) : null}

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1.3fr]">
        <Panel title="Headline sparkline">
          <Sparkline points={(headline?.history ?? []).slice(-24).map((point) => ({ month: point.month, value: point.saMm }))} />
          <div className="mt-2 text-sm text-muted">Last 24 months of all-items SA m/m movement.</div>
        </Panel>
        <Panel title={`Latest contribution waterfall, ${formatMonth(data.refMonth)}`}>
          <ContributionWaterfall rows={data.topContributors} />
        </Panel>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <Panel title="Last 3 months table">
          <LatestRowsTable entries={latestRows} />
        </Panel>
        <Panel title="Food, energy, shelter, and sector summary">
          <div className="space-y-3">
            {groups.map((entry) => (
              <div key={entry!.itemCode} className="grid grid-cols-[1fr_auto_auto] items-center gap-3 border-b border-line pb-2 last:border-0">
                <div>
                  <div className="font-medium">{entry!.name}</div>
                  <div className="text-xs text-muted">{entry!.itemCode}</div>
                </div>
                <div className="text-right text-sm">{formatWeight(entry!.currentRi)}</div>
                <div className="text-right text-sm">{formatPercent(entry!.latest.saMm)}</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
