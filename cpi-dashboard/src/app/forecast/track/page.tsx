import { ScoreWaterfall } from "@/components/Charts";
import { ForecastNav } from "@/components/ForecastNav";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getBacktests, getForecast, getScore } from "@/lib/data";
import { formatMonth, formatPercent, formatPp } from "@/lib/format";

export default function ForecastTrackPage() {
  const forecast = getForecast();
  const score = getScore();
  const backtest = getBacktests().C;
  return (
    <>
      <PageTitle eyebrow="Forecast Track" title="Forecast versus published CPI">
        Tracks uploaded forecasts against the actual BLS print once `score.json` is available.
      </PageTitle>
      <ForecastNav active="track" />
      {!forecast ? (
        <Panel title="No forecast uploaded">
          <p className="text-sm text-muted">Upload a forecast run to populate the track.</p>
        </Panel>
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <MetricCard label="Forecast month" value={formatMonth(forecast.forecastMonth)} subvalue={`Generated ${forecast.generatedAt}`} />
            <MetricCard label="Forecast headline SA" value={formatPercent(forecast.headline.saMm)} subvalue="P50" />
            <MetricCard label="Score status" value={score?.status ?? "none"} subvalue={score?.month ? formatMonth(score.month) : "no score uploaded"} />
            <MetricCard label="Modern MAE" value={formatPercent(backtest.metrics.headlineNsaMae)} subvalue="window C seeded diagnostic" />
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <Panel title="Latest score">
              {score?.headline ? (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span>Forecast SA m/m</span><span>{formatPercent(score.headline.forecastSaMm)}</span></div>
                  <div className="flex justify-between"><span>Actual SA m/m</span><span>{formatPercent(score.headline.actualSaMm)}</span></div>
                  <div className="flex justify-between"><span>Miss</span><span>{formatPp(score.headline.missSaPp)}</span></div>
                </div>
              ) : (
                <p className="text-sm text-muted">The June 2026 actual is not available in the local cache yet. This page will update after scoring.</p>
              )}
            </Panel>
            <Panel title="Error attribution waterfall">
              <ScoreWaterfall rows={score?.rows ?? []} />
            </Panel>
          </div>
        </>
      )}
      <div className="mt-4 text-xs text-muted">Model output, not BLS data. Actuals: U.S. Bureau of Labor Statistics.</div>
    </>
  );
}
