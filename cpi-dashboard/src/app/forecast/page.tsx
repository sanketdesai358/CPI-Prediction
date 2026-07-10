import Link from "next/link";
import { ForecastTable } from "@/components/ForecastTable";
import { ForecastNav } from "@/components/ForecastNav";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, getFeedHealth, getForecast } from "@/lib/data";
import { formatMonth, formatPercent } from "@/lib/format";

function statusLabel(status: string) {
  return status.replaceAll("_", " ");
}

export default function ForecastPage() {
  const forecast = getForecast();
  const feedHealth = getFeedHealth();
  const data = getDashboardData();
  if (!forecast) {
    return (
      <Panel title="No forecast uploaded">
        <p className="text-sm text-muted">Upload `forecast.json` to the forecast data store to populate this page.</p>
      </Panel>
    );
  }
  const countdownDate = new Date(`${data.nextRelease.releaseDate}T12:30:00Z`);
  const days = Math.max(0, Math.ceil((countdownDate.valueOf() - Date.now()) / 86_400_000));
  const saRanges: Array<{ label: string; p10: number | null; p50: number | null; p90: number | null; note?: string }> = [
    {
      label: "Headline SA m/m",
      p10: forecast.headline.saInterval.p10,
      p50: forecast.headline.saMm,
      p90: forecast.headline.saInterval.p90
    },
    {
      label: "Core SA m/m",
      p10: forecast.core.saInterval.p10,
      p50: forecast.core.saMm,
      p90: forecast.core.saInterval.p90
    },
    {
      label: "Headline SA y/y",
      p10: null,
      p50: forecast.headline.saYoy ?? null,
      p90: null,
      note: "implied by forecast SA index"
    },
    {
      label: "Headline NSA y/y",
      p10: null,
      p50: forecast.headline.nsaYoy,
      p90: null,
      note: "implied by forecast NSA index"
    },
    {
      label: "Core SA y/y",
      p10: null,
      p50: forecast.core.saYoy ?? null,
      p90: null,
      note: "implied by forecast SA index"
    },
    {
      label: "Core NSA y/y",
      p10: null,
      p50: forecast.core.nsaYoy,
      p90: null,
      note: "implied by forecast NSA index"
    }
  ];
  const topDrivers = forecast.components.slice(0, 8);
  return (
    <>
      <PageTitle eyebrow="Forecast" title={`Next CPI print: ${formatMonth(forecast.forecastMonth)}`}>
        Model output, not BLS data. Actuals remain sourced from the U.S. Bureau of Labor Statistics.
      </PageTitle>
      <ForecastNav active="forecast" />
      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <section className="rounded border border-line bg-white p-5 shadow-subtle">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-muted">Headline SA m/m</div>
              <div className="mt-2 text-4xl font-semibold tracking-tight text-ink">{formatPercent(forecast.headline.saMm)}</div>
              <div className="mt-2 text-sm text-muted">
                y/y: SA {formatPercent(forecast.headline.saYoy)} / NSA {formatPercent(forecast.headline.nsaYoy)}
              </div>
              <div className="mt-1 text-sm text-muted">
                P10 {formatPercent(forecast.headline.saInterval.p10)} · P90 {formatPercent(forecast.headline.saInterval.p90)}
              </div>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-muted">Core SA m/m</div>
              <div className="mt-2 text-4xl font-semibold tracking-tight text-ink">{formatPercent(forecast.core.saMm)}</div>
              <div className="mt-2 text-sm text-muted">
                y/y: SA {formatPercent(forecast.core.saYoy)} / NSA {formatPercent(forecast.core.nsaYoy)}
              </div>
              <div className="mt-1 text-sm text-muted">
                P10 {formatPercent(forecast.core.saInterval.p10)} · P90 {formatPercent(forecast.core.saInterval.p90)}
              </div>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-muted">Release</div>
              <div className="mt-2 text-4xl font-semibold tracking-tight text-ink">{days}</div>
              <div className="mt-1 text-sm text-muted">days · {data.nextRelease.releaseDate} {data.nextRelease.releaseTime}</div>
            </div>
          </div>
          <div className="mt-5 grid gap-3 border-t border-line pt-4 md:grid-cols-3">
            <div className="rounded bg-wash p-3">
              <div className="text-xs text-muted">Headline SA P10</div>
              <div className="text-lg font-semibold">{formatPercent(forecast.headline.saInterval.p10)}</div>
            </div>
            <div className="rounded bg-wash p-3">
              <div className="text-xs text-muted">Headline SA P90</div>
              <div className="text-lg font-semibold">{formatPercent(forecast.headline.saInterval.p90)}</div>
            </div>
            <div className="rounded bg-wash p-3">
              <div className="text-xs text-muted">Data through</div>
              <div className="text-lg font-semibold">{formatMonth(forecast.dataThrough)}</div>
            </div>
          </div>
        </section>
        <Panel title="How to read this">
          <div className="space-y-3 text-sm text-muted">
            <p>
              The large numbers are the model median for the next CPI print. The P10/P90 range is the
              model uncertainty band, not a BLS range.
            </p>
            <p>
              Contributions below are in percentage points of headline. Positive rows push CPI higher;
              negative rows pull it lower.
            </p>
            <p className="font-medium text-ink">Model output, not BLS data.</p>
          </div>
        </Panel>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1fr]">
        {feedHealth ? (
          <Panel title="Feed health">
            <div className="grid gap-2 text-sm sm:grid-cols-3">
              <div className="rounded bg-wash p-3">
                <div className="text-xs uppercase text-muted">Live</div>
                <div className="text-2xl font-semibold text-ink">{feedHealth.summary.live}</div>
              </div>
              <div className="rounded bg-wash p-3">
                <div className="text-xs uppercase text-muted">Partial</div>
                <div className="text-2xl font-semibold text-ink">{feedHealth.summary.partial}</div>
              </div>
              <div className="rounded bg-wash p-3">
                <div className="text-xs uppercase text-muted">Fallback / blocked</div>
                <div className="text-2xl font-semibold text-ink">{feedHealth.summary.fallbackOrBlocked}</div>
              </div>
            </div>
            <div className="mt-3 max-h-80 overflow-y-auto rounded border border-line">
              <table className="min-w-full text-left text-xs">
                <thead className="border-b border-line bg-wash uppercase text-muted">
                  <tr>
                    <th className="px-3 py-2">Component</th>
                    <th className="px-3 py-2">Status</th>
                    <th className="px-3 py-2">Last obs</th>
                    <th className="px-3 py-2">Input values</th>
                  </tr>
                </thead>
                <tbody>
                  {feedHealth.components.map((row) => (
                    <tr key={row.itemCode} className="border-b border-line/70 align-top">
                      <td className="px-3 py-2">
                        <div className="font-medium text-ink">{row.name}</div>
                        <div className="text-muted">{row.primaryFeed}</div>
                      </td>
                      <td className="px-3 py-2">
                        <span className={`rounded px-2 py-1 ${row.fallbackUsed ? "bg-amber-50 text-amber-800" : "bg-teal/10 text-teal"}`}>
                          {statusLabel(row.status)}
                        </span>
                      </td>
                      <td className="px-3 py-2">{row.lastObservationDate ?? "n/a"}</td>
                      <td className="max-w-[320px] px-3 py-2 text-muted">
                        {row.observationsUsed.length
                          ? row.observationsUsed.map((obs) => `${obs.label}: ${obs.value}`).join("; ")
                          : row.details}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-2 text-xs text-muted">
              A fallback flag means the dashboard is not using a complete live feed for that component yet.
            </p>
          </Panel>
        ) : null}
        <Panel title="SA forecast ranges">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr><th className="py-2 pr-4">Series</th><th className="py-2 pr-4">P10</th><th className="py-2 pr-4">P50</th><th className="py-2 pr-4">P90</th></tr>
              </thead>
              <tbody>
                {saRanges.map((row) => (
                  <tr key={row.label} className="border-b border-line/70">
                    <td className="py-2 pr-4">{row.label}</td>
                    <td className="py-2 pr-4">{formatPercent(row.p10)}</td>
                    <td className="py-2 pr-4">
                      {formatPercent(row.p50)}
                      {row.note ? <div className="text-xs text-muted">{row.note}</div> : null}
                    </td>
                    <td className="py-2 pr-4">{formatPercent(row.p90)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">Intervals are model uncertainty bands around seasonally adjusted m/m forecasts. Y/y rows are implied levels without a separate uncertainty band.</p>
        </Panel>
        <Panel title="Top forecast drivers">
          <div className="space-y-2">
            {topDrivers.map((row) => (
              <Link key={row.itemCode} href={`/components/${row.itemCode}`} className="grid grid-cols-[1fr_auto] gap-3 rounded border border-line p-2 hover:border-teal">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{row.name}</div>
                  <div className="truncate text-xs text-muted">Tier {row.tier} · {row.modelType}</div>
                </div>
                <div className="text-right text-sm font-semibold">{row.contribution_pp >= 0 ? "+" : ""}{row.contribution_pp.toFixed(2)} pp</div>
              </Link>
            ))}
          </div>
          <Link className="mt-3 inline-block text-sm font-medium text-teal hover:underline" href="/forecast/track">
            Open forecast-vs-actual track
          </Link>
          <Link className="ml-4 mt-3 inline-block text-sm font-medium text-teal hover:underline" href="/forecast/model-divergence">
            Open model divergence
          </Link>
        </Panel>
      </div>
      {forecast.foodForwardPath ? (
        <div className="mt-4">
          <Panel title="Food forward path">
            <div className="mb-3 rounded bg-wash p-3 text-sm text-muted">
              <div className="font-medium text-ink">Model output, not BLS data.</div>
              <div>{forecast.foodForwardPath.note}</div>
              <div className="mt-1 text-xs uppercase">Futures status: {statusLabel(forecast.foodForwardPath.status)}</div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-line text-xs uppercase text-muted">
                  <tr>
                    <th className="py-2 pr-4">Horizon</th>
                    <th className="py-2 pr-4">Food m/m</th>
                    <th className="py-2 pr-4">P10 / P90</th>
                    <th className="py-2 pr-4">Headline contribution</th>
                    <th className="py-2 pr-4">Largest food drivers</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.foodForwardPath.horizons.map((row) => (
                    <tr key={row.horizon} className="border-b border-line/70 align-top">
                      <td className="py-2 pr-4 font-medium">{row.label}</td>
                      <td className="py-2 pr-4">{formatPercent(row.foodNsaMm)}</td>
                      <td className="py-2 pr-4 text-muted">
                        {formatPercent(row.interval.p10)} / {formatPercent(row.interval.p90)}
                      </td>
                      <td className="py-2 pr-4">{row.headlineContributionPp.toFixed(3)} pp</td>
                      <td className="max-w-[520px] py-2 pr-4 text-muted">
                        {row.components
                          .slice(0, 4)
                          .map((item) => `${item.name}: ${item.contributionPp.toFixed(3)} pp`)
                          .join("; ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {forecast.foodForwardPath.lagReport?.rows?.length ? (
              <div className="mt-4 grid gap-2 md:grid-cols-2">
                {forecast.foodForwardPath.lagReport.rows.map((row) => (
                  <div key={row.component} className="rounded border border-line p-3 text-xs">
                    <div className="font-semibold text-ink">{row.component}</div>
                    <div className="text-muted">Features: {row.features.join(", ")}</div>
                    <div className="text-muted">Expected lag peak: {row.expectedLagPeak}</div>
                    <div className={row.kept ? "text-teal" : "text-amber-700"}>{statusLabel(row.decision)}</div>
                  </div>
                ))}
              </div>
            ) : null}
          </Panel>
        </div>
      ) : null}
      <div className="mt-4">
        <Panel title="Full component forecast table">
          <ForecastTable rows={forecast.components} />
        </Panel>
      </div>
      <div className="mt-4 text-xs text-muted">Model output, not BLS data. Actuals: U.S. Bureau of Labor Statistics.</div>
    </>
  );
}
