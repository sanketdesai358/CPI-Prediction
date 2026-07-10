import { ContributionExplorer } from "@/components/Charts";
import { PageTitle, Panel } from "@/components/Shell";
import { getDashboardData } from "@/lib/data";

export default function ContributionsPage() {
  const data = getDashboardData();
  const headline = data.entries.find((entry) => entry.itemCode === "SA0");
  const headlineByMonth = Object.fromEntries(
    (headline?.history ?? []).map((point) => [point.month, point.saMm] as const)
  );
  return (
    <>
      <PageTitle eyebrow="Contributions" title="Reconcile components to the headline m/m change">
        Toggle between major groups and lower-level components. The residual shows the visible-row reconciliation
        difference versus published all-items SA m/m.
      </PageTitle>
      <Panel title="Contribution waterfall">
        <ContributionExplorer entries={data.entries} months={data.latestMonths} headlineByMonth={headlineByMonth} />
      </Panel>
    </>
  );
}
