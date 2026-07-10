import { ChallengerBanner, ChallengerMajorComponentsTable } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger } from "@/lib/data";

export default function ChallengerMajorComponentsPage() {
  const result = getChallenger();
  if (!result) {
    return (
      <>
        <ChallengerBanner />
        <Panel title="No challenger run uploaded">
          <p className="text-sm text-muted">Run the challenger backtest to generate major-component diagnostics.</p>
        </Panel>
      </>
    );
  }
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger" title="Major Component Misses">
        Major published CPI aggregates with June forecasts, latest actual-month errors, and Window C MAE. Error is model prediction minus actual, shown in percentage points.
      </PageTitle>
      <Panel title="Major components">
        <ChallengerMajorComponentsTable diagnostics={result.majorComponentDiagnostics ?? []} current={result.currentForecast} />
      </Panel>
    </>
  );
}
