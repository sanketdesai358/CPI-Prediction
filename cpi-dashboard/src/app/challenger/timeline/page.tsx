import { ChallengerBanner, ChallengerModelDefinitions, ModelComparisonTimeline } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getModelComparison } from "@/lib/data";
import { formatPercent } from "@/lib/format";

export default function ChallengerTimelinePage() {
  const result = getModelComparison();
  if (!result) {
    return (
      <>
        <ChallengerBanner />
        <Panel title="No timeline artifact">
          <p className="text-sm text-muted">Run `python analysis/model_comparison/build_timeline.py --dashboard` in cpi-model to generate the model comparison timeline.</p>
        </Panel>
      </>
    );
  }
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger" title="Actual vs Model Timeline">
        Headline CPI actuals against walk-forward one-step-ahead model predictions. Y/y uses the nowcaster convention: 11 actual months plus 1 forecast month.
      </PageTitle>
      <div className="grid gap-4">
        <Panel title="Model definitions">
          <ChallengerModelDefinitions />
        </Panel>
        <Panel title="Interactive timeline">
          <ModelComparisonTimeline result={result} />
        </Panel>
        <Panel title="Availability and MAE table">
          <div className="mb-3 rounded bg-wash p-3 text-sm text-muted">
            Production Tier 1 and Tier 3 fallback formulas are included as walk-forward baselines. The full live-feed production model remains omitted until a true historical replay exists. Common-span metrics start at {result.commonStart}; only rows shared by the displayed models are directly comparable.
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr>
                  <th className="py-2 pr-4">Model</th>
                  <th className="py-2 pr-4">Start</th>
                  <th className="py-2 pr-4">End</th>
                  <th className="py-2 pr-4">Months</th>
                  <th className="py-2 pr-4">Full SA m/m MAE</th>
                  <th className="py-2 pr-4">Full SA y/y MAE</th>
                  <th className="py-2 pr-4">Common SA m/m MAE</th>
                  <th className="py-2 pr-4">Common SA y/y MAE</th>
                </tr>
              </thead>
              <tbody>
                {result.summary.map((row) => (
                  <tr key={row.model} className="border-b border-line/70">
                    <td className="py-2 pr-4 font-medium">{row.label}</td>
                    <td className="py-2 pr-4">{row.start ?? "n/a"}</td>
                    <td className="py-2 pr-4">{row.end ?? "n/a"}</td>
                    <td className="py-2 pr-4">{row.months}</td>
                    <td className="py-2 pr-4">{formatPercent(row.fullSaMmMae ?? null, 3)}</td>
                    <td className="py-2 pr-4">{formatPercent(row.fullSaYoyMae ?? null, 3)}</td>
                    <td className="py-2 pr-4">{formatPercent(row.commonSaMmMae ?? null, 3)}</td>
                    <td className="py-2 pr-4">{formatPercent(row.commonSaYoyMae ?? null, 3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
        {result.notes.length ? (
          <Panel title="Artifact notes">
            <ul className="space-y-2 text-sm text-muted">
              {result.notes.map((note) => <li key={note}>{note}</li>)}
            </ul>
          </Panel>
        ) : null}
      </div>
    </>
  );
}
