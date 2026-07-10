import Link from "next/link";
import { notFound } from "next/navigation";
import { ChallengerBanner, ChallengerComponentChart } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger, getComponent } from "@/lib/data";
import { formatPercent } from "@/lib/format";

export default async function ChallengerComponentPage({ params }: { params: Promise<{ itemCode: string }> }) {
  const resolvedParams = await params;
  const itemCode = decodeURIComponent(resolvedParams.itemCode);
  const component = getComponent(itemCode);
  const result = getChallenger();
  if (!component) notFound();
  const leagueRow = result?.componentLeague.find((row) => row.itemCode === itemCode);
  const rows = result?.componentSeries[itemCode] ?? [];
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger component" title={component.name}>
        Actual NSA m/m overlaid against production, HRNN, I-GRU, and seasonal AR challenger predictions.
      </PageTitle>
      <div className="mb-4 flex flex-wrap gap-3 text-sm">
        <Link href={`/components/${encodeURIComponent(itemCode)}`} className="font-medium text-teal hover:underline">
          Open production component detail
        </Link>
        <Link href="/challenger/components" className="font-medium text-teal hover:underline">
          Back to challenger table
        </Link>
      </div>
      <Panel title="True vs predicted">
        <ChallengerComponentChart rows={rows} />
      </Panel>
      <div className="mt-4">
        <Panel title="Window C MAE">
          {leagueRow ? (
            <div className="grid gap-3 text-sm md:grid-cols-4">
              <div className="rounded bg-wash p-3"><div className="text-xs uppercase text-muted">Production</div><div className="text-lg font-semibold">{formatPercent(leagueRow.productionMae)}</div></div>
              <div className="rounded bg-wash p-3"><div className="text-xs uppercase text-muted">HRNN</div><div className="text-lg font-semibold">{formatPercent(leagueRow.hrnnMae)}</div></div>
              <div className="rounded bg-wash p-3"><div className="text-xs uppercase text-muted">I-GRU</div><div className="text-lg font-semibold">{formatPercent(leagueRow.iGruMae)}</div></div>
              <div className="rounded bg-wash p-3"><div className="text-xs uppercase text-muted">Seasonal AR</div><div className="text-lg font-semibold">{formatPercent(leagueRow.seasonalArMae)}</div></div>
            </div>
          ) : (
            <p className="text-sm text-muted">This component was not included in the challenger league table.</p>
          )}
        </Panel>
      </div>
    </>
  );
}
