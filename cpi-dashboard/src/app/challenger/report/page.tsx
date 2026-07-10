import Link from "next/link";
import { ChallengerBanner } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger } from "@/lib/data";

export default function ChallengerReportPage() {
  const result = getChallenger();
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger" title="Comparison Report">
        Full local Markdown report is written by the model runner at `cpi-model/challenger/hrnn/comparison.md`.
      </PageTitle>
      {result ? (
        <div className="grid gap-4">
          <Panel title="Implementation status">
            <p className="text-sm text-muted">{result.implementationStatus}</p>
          </Panel>
          <Panel title="Adoption candidates">
            {result.adoptionCandidates.length ? (
              <ul className="space-y-2 text-sm text-muted">
                {result.adoptionCandidates.map((row) => (
                  <li key={row.itemCode}>
                    <Link href={`/challenger/${row.itemCode}`} className="font-medium text-teal hover:underline">
                      {row.itemCode} {row.name}
                    </Link>
                    : {row.evidence}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">No candidates met the current evidence rule.</p>
            )}
          </Panel>
          <Panel title="Honest notes">
            <ul className="space-y-2 text-sm text-muted">
              {result.honestNotes.map((note) => <li key={note}>{note}</li>)}
            </ul>
          </Panel>
        </div>
      ) : (
        <Panel title="No report data uploaded">
          <p className="text-sm text-muted">Run the challenger backtest to generate comparison artifacts.</p>
        </Panel>
      )}
    </>
  );
}
