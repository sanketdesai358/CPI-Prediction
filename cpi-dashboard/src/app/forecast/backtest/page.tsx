import { BacktestRollingChart } from "@/components/Charts";
import { PageTitle, Panel } from "@/components/Shell";
import { getBacktests } from "@/lib/data";
import { formatPercent } from "@/lib/format";

const labels: Record<string, string> = {
  A: "A: Long-run statistical",
  B: "B: Full system",
  C: "C: Modern regime"
};

export default function ForecastBacktestPage() {
  const backtests = getBacktests();
  return (
    <>
      <PageTitle eyebrow="Backtest" title="Three-window model diagnostics">
        Seeded dashboard diagnostics render now; decision-grade claims require archived RI vintages and real-time external-feed snapshots.
      </PageTitle>
      <div className="grid gap-4">
        {(["A", "B", "C"] as const).map((key) => {
          const result = backtests[key];
          return (
            <Panel key={key} title={labels[key]}>
              <div className="mb-3 grid gap-3 md:grid-cols-5">
                <div className="rounded border border-line p-3 text-sm"><div className="text-muted">Available span</div><div className="font-medium">{result.availableStart} to {result.availableEnd}</div></div>
                <div className="rounded border border-line p-3 text-sm"><div className="text-muted">Model MAE</div><div className="font-medium">{formatPercent(result.metrics.headlineNsaMae)}</div></div>
                <div className="rounded border border-line p-3 text-sm"><div className="text-muted">Seasonal RW</div><div className="font-medium">{formatPercent(result.metrics.seasonalRwMae)}</div></div>
                <div className="rounded border border-line p-3 text-sm"><div className="text-muted">AR(1)</div><div className="font-medium">{formatPercent(result.metrics.ar1Mae)}</div></div>
                <div className="rounded border border-line p-3 text-sm"><div className="text-muted">P10-P90 coverage</div><div className="font-medium">{formatPercent(result.metrics.intervalCoverage, 0)}</div></div>
              </div>
              <BacktestRollingChart result={result} />
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b border-line text-xs uppercase text-muted">
                    <tr><th className="py-2 pr-4">Component</th><th className="py-2 pr-4">MAE</th><th className="py-2 pr-4">Benchmark</th><th className="py-2 pr-4">Note</th></tr>
                  </thead>
                  <tbody>
                    {result.componentLeague.map((row) => (
                      <tr key={row.itemCode} className="border-b border-line/70">
                        <td className="py-2 pr-4">{row.name}</td>
                        <td className="py-2 pr-4">{formatPercent(row.mae)}</td>
                        <td className="py-2 pr-4">{formatPercent(row.benchmarkMae)}</td>
                        <td className="py-2 pr-4 text-muted">{row.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {result.commodityComplex?.rows?.length ? (
                <div className="mt-4 overflow-x-auto">
                  <div className="mb-2 text-sm font-semibold">Food commodity-complex comparison</div>
                  <table className="min-w-full text-left text-sm">
                    <thead className="border-b border-line text-xs uppercase text-muted">
                      <tr><th className="py-2 pr-4">Component</th><th className="py-2 pr-4">Complex</th><th className="py-2 pr-4">With granular</th><th className="py-2 pr-4">Composite only</th><th className="py-2 pr-4">Winner</th><th className="py-2 pr-4">AP-CPI corr</th></tr>
                    </thead>
                    <tbody>
                      {result.commodityComplex.rows.map((row) => (
                        <tr key={row.itemCode} className="border-b border-line/70 align-top">
                          <td className="py-2 pr-4">{row.name}</td>
                          <td className="py-2 pr-4">{row.complex}</td>
                          <td className="py-2 pr-4">{formatPercent(row.withGranularMae)}</td>
                          <td className="py-2 pr-4">{formatPercent(row.withoutGranularMae)}</td>
                          <td className="py-2 pr-4 text-muted">{row.winner.replaceAll("_", " ")}</td>
                          <td className="py-2 pr-4">{row.validation.apCpiCorrelation === null ? "n/a" : row.validation.apCpiCorrelation.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </Panel>
          );
        })}
      </div>
      <div className="mt-4 text-xs text-muted">Model output, not BLS data. Actuals: U.S. Bureau of Labor Statistics.</div>
    </>
  );
}
