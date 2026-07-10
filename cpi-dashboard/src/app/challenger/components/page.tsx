import { ChallengerBanner, ChallengerLeagueTable } from "@/components/Challenger";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger } from "@/lib/data";

export default function ChallengerComponentsPage() {
  const result = getChallenger();
  return (
    <>
      <ChallengerBanner />
      <PageTitle eyebrow="Challenger" title="Component League Table">
        Window C component MAE comparison, sorted by current weight times absolute MAE gap by default.
      </PageTitle>
      <Panel>
        <ChallengerLeagueTable rows={result?.componentLeague ?? []} />
      </Panel>
    </>
  );
}
