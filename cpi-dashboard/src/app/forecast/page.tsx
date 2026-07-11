import Link from "next/link";
import { ForecastTable } from "@/components/ForecastTable";
import { ForecastNav } from "@/components/ForecastNav";
import { PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, getForecast } from "@/lib/data";
import { formatMonth, formatPercent } from "@/lib/format";

export default function ForecastPage() {
  const forecast = getForecast();
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
      <div className="mt-4">
        <Panel title="Full component forecast table">
          <ForecastTable rows={forecast.components} />
        </Panel>
      </div>
      <div className="mt-4 text-xs text-muted">Model output, not BLS data. Actuals: U.S. Bureau of Labor Statistics.</div>
    </>
  );
}
