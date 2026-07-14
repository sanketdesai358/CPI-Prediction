import { ScoreWaterfall } from "@/components/Charts";
import { ForecastNav } from "@/components/ForecastNav";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getBacktests, getForecast, getModelComparison, getScore } from "@/lib/data";
import { formatMonth, formatPercent, formatPp } from "@/lib/format";

export default function ForecastTrackPage() {
  const forecast = getForecast();
  const score = getScore();
  const backtest = getBacktests().C;
  const comparison = getModelComparison();
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
            <Panel title="June 2026 model comparison">
              {comparison ? (
                <div className="overflow-x-auto text-sm">
                  <table className="w-full">
                    <thead><tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted"><th className="py-2 pr-3">Model</th><th className="py-2 pr-3">SA m/m</th><th className="py-2 pr-3">SA y/y</th><th className="py-2">Availability</th></tr></thead>
                    <tbody>
                      {comparison.summary.map((model) => {
                        const row = comparison.rows.find((candidate) => candidate.month === score?.month);
                        const key = model.model as keyof typeof row;
                        const mm = row?.[`${String(key)}SaMm` as keyof typeof row] as number | null | undefined;
                        const yoy = row?.[`${String(key)}SaYoy` as keyof typeof row] as number | null | undefined;
                        return <tr key={model.model} className="border-b border-line"><td className="py-2 pr-3 font-medium">{model.label}</td><td className="py-2 pr-3">{formatPercent(mm)}</td><td className="py-2 pr-3">{formatPercent(yoy)}</td><td className="py-2">{model.end === score?.month ? "June scored" : model.end ? `through ${formatMonth(model.end)}` : "no archived value"}</td></tr>;
                      })}
                    </tbody>
                  </table>
                  <p className="mt-3 text-xs text-muted">June is shown only where a pre-release walk-forward prediction exists. Missing challenger values are not backfilled after the release.</p>
                </div>
              ) : <p className="text-sm text-muted">Model comparison artifact unavailable.</p>}
            </Panel>
            <Panel title="Error attribution waterfall">
              <ScoreWaterfall rows={score?.rows ?? []} />
            </Panel>
          </div>
          {score?.summary ? (
            <Panel title="Post-release scoring coverage" className="mt-4">
              <p className="text-sm text-muted">{score.summary.scoredComponentCount} of {score.summary.componentCount} components scored. {score.summary.liveFeedCount} used live feeds and {score.summary.fallbackCount} used an explicit feed fallback.</p>
            </Panel>
          ) : null}
        </>
      )}
      <div className="mt-4 text-xs text-muted">Model output, not BLS data. Actuals: U.S. Bureau of Labor Statistics.</div>
    </>
  );
}
