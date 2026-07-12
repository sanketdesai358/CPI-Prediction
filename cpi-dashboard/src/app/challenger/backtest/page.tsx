import { ChallengerBanner, ChallengerModelDefinitions, ChallengerRollingChart } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger } from "@/lib/data";
import { formatPercent } from "@/lib/format";

const windows = ["A", "B", "C"] as const;
const variants = [
  ["productionTier1", "Tier 1 fallback"],
  ["productionTier3", "Tier 3 fallback"],
  ["hrnn", "HRNN"],
  ["iGru", "I-GRU"],
  ["seasonalAr", "Seasonal AR"]
] as const;

export default function ChallengerBacktestPage() {
  const result = getChallenger();
  if (!result) {
    return (
      <>
        <ChallengerBanner />
        <Panel title="No challenger backtest uploaded">
          <p className="text-sm text-muted">The challenger tab will populate after a precomputed run is copied to the dashboard data store.</p>
        </Panel>
      </>
    );
  }
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger" title="Backtest">
        Window A/B/C full-window MAE and RMSE summaries, plus trailing 24-month MAE and hierarchy-level normalized error diagnostics.
      </PageTitle>
      <div className="grid gap-4">
        <Panel title="Model definitions">
          <ChallengerModelDefinitions />
        </Panel>
        {windows.map((window) => {
          const item = result.windows[window];
          return (
            <Panel key={window} title={`Window ${window}: ${item.availableStart ?? item.requestedStart} to ${item.availableEnd ?? "n/a"}`}>
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b border-line text-xs uppercase text-muted">
                    <tr><th className="py-2 pr-4">Model</th><th className="py-2 pr-4">Headline NSA<br />MAE / RMSE</th><th className="py-2 pr-4">Headline SA<br />MAE / RMSE</th><th className="py-2 pr-4">Core NSA<br />MAE / RMSE</th><th className="py-2 pr-4">Core SA<br />MAE / RMSE</th></tr>
                  </thead>
                  <tbody>
                    {variants.map(([key, label]) => (
                      <tr key={key} className="border-b border-line/70">
                        <td className="py-2 pr-4 font-medium">{label}</td>
                        <td className="py-2 pr-4">{formatPercent(item.metrics[`${key}HeadlineNsaMmMae`], 3)} / {formatPercent(item.metrics[`${key}HeadlineNsaMmRmse`], 3)}</td>
                        <td className="py-2 pr-4">{formatPercent(item.metrics[`${key}HeadlineSaMmMae`], 3)} / {formatPercent(item.metrics[`${key}HeadlineSaMmRmse`], 3)}</td>
                        <td className="py-2 pr-4">{formatPercent(item.metrics[`${key}CoreNsaMmMae`], 3)} / {formatPercent(item.metrics[`${key}CoreNsaMmRmse`], 3)}</td>
                        <td className="py-2 pr-4">{formatPercent(item.metrics[`${key}CoreSaMmMae`], 3)} / {formatPercent(item.metrics[`${key}CoreSaMmRmse`], 3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
          );
        })}
        <Panel title="Window C trailing 24-month MAE">
          <ChallengerRollingChart rolling24={result.windows.C.rolling24} includeLegacyProxy={false} />
        </Panel>
        <Panel title="Hierarchy-level normalized error">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr><th className="py-2 pr-4">Level</th><th className="py-2 pr-4">Components</th><th className="py-2 pr-4">HRNN MAE</th><th className="py-2 pr-4">Seasonal AR MAE</th><th className="py-2 pr-4">HRNN / seasonal AR</th></tr>
              </thead>
              <tbody>
                {result.hierarchyLevelMetrics.map((row) => (
                  <tr key={row.level} className="border-b border-line/70">
                    <td className="py-2 pr-4">{row.level}</td>
                    <td className="py-2 pr-4">{row.components}</td>
                    <td className="py-2 pr-4">{formatPercent(row.hrnnMae)}</td>
                    <td className="py-2 pr-4">{formatPercent(row.seasonalArMae)}</td>
                    <td className="py-2 pr-4">{row.normalizedVsSeasonalAr === null ? "n/a" : row.normalizedVsSeasonalAr.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </>
  );
}
