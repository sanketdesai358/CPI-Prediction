import Link from "next/link";
import { ChallengerBanner, ChallengerCurrentForecastTable, ChallengerModelDefinitions, ChallengerRollingChart } from "@/components/Challenger";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getChallenger } from "@/lib/data";
import { formatPercent } from "@/lib/format";

function metric(result: NonNullable<ReturnType<typeof getChallenger>>, key: string) {
  return result.windows.C.metrics[key] ?? null;
}

export default function ChallengerPage() {
  const result = getChallenger();
  if (!result) {
    return (
      <>
        <ChallengerBanner />
        <Panel title="No challenger run uploaded">
          <p className="text-sm text-muted">Run the HRNN challenger backtest and upload `src/data/challenger/results.json` to populate this tab.</p>
        </Panel>
      </>
    );
  }
  const scoreboard = [
    { label: "Tier 1 fallback", value: metric(result, "productionTier1HeadlineNsaMmMae") },
    { label: "Tier 3 fallback", value: metric(result, "productionTier3HeadlineNsaMmMae") },
    { label: "HRNN", value: metric(result, "hrnnHeadlineNsaMmMae") },
    { label: "I-GRU", value: metric(result, "iGruHeadlineNsaMmMae") },
    { label: "Seasonal AR", value: metric(result, "seasonalArHeadlineNsaMmMae") }
  ];
  return (
    <>
      <ChallengerBanner />
      <Panel title="Model definitions">
        <ChallengerModelDefinitions />
      </Panel>
      <PageTitle eyebrow="Challenger" title="Model Research Comparison">
        A precomputed research run comparing HRNN, I-GRU, seasonal AR, and fallback baselines. It is not a second production forecast.
      </PageTitle>
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        {scoreboard.map((row) => (
          <MetricCard key={row.label} label={`${row.label} window C headline MAE`} value={formatPercent(row.value, 3)} />
        ))}
      </div>
      <div className="mt-4">
        <Panel title="Current forecast month comparison">
          <ChallengerCurrentForecastTable current={result.currentForecast} />
        </Panel>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Panel title="Trailing 24-month MAE, window C">
          <ChallengerRollingChart result={result} />
        </Panel>
        <Panel title="Read this first">
          <div className="space-y-3 text-sm text-muted">
            <p>{result.implementationStatus}</p>
            <p>Generated {result.generatedAt}. Runtime {result.runtime.seconds.toFixed(1)} seconds.</p>
            <Link href="/challenger/report" className="font-medium text-teal hover:underline">
              Open the full challenger report
            </Link>
          </div>
        </Panel>
      </div>
      <div className="mt-4 grid gap-4 md:grid-cols-4">
        <Link href="/challenger/timeline" className="rounded border border-line bg-white p-4 shadow-subtle hover:border-teal">
          <div className="font-semibold">Actual vs model timeline</div>
          <div className="mt-1 text-sm text-muted">Full-span and 2022+ charts for m/m and y/y predictions.</div>
        </Link>
        <Link href="/challenger/components" className="rounded border border-line bg-white p-4 shadow-subtle hover:border-teal">
          <div className="font-semibold">Component league table</div>
          <div className="mt-1 text-sm text-muted">Filter HRNN wins, I-GRU wins, seasonal AR wins, and ties.</div>
        </Link>
        <Link href="/challenger/backtest" className="rounded border border-line bg-white p-4 shadow-subtle hover:border-teal">
          <div className="font-semibold">Backtest details</div>
          <div className="mt-1 text-sm text-muted">Windows A/B/C and hierarchy-level breakdowns.</div>
        </Link>
        <Link href="/forecast" className="rounded border border-line bg-white p-4 shadow-subtle hover:border-teal">
          <div className="font-semibold">Production forecast</div>
          <div className="mt-1 text-sm text-muted">Return to the actual production nowcast surface.</div>
        </Link>
      </div>
    </>
  );
}
