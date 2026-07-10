import { ComponentExplorer } from "@/components/Charts";
import { LatestRowsTable } from "@/components/DataTable";
import { PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, sortByWeight } from "@/lib/data";

export default function ComponentsPage() {
  const data = getDashboardData();
  const weighted = sortByWeight(data.entries.filter((entry) => entry.currentRi !== null && entry.itemCode !== "SA0"));
  return (
    <>
      <PageTitle eyebrow="Explorer" title="Component weights and latest inflation">
        Tile size follows current price-updated relative importance. Color follows the latest inflation rate.
        Click any component to open the detail page with methodology and full history.
      </PageTitle>
      <Panel title="Weighted component map">
        <ComponentExplorer entries={weighted} />
      </Panel>
      <div className="mt-4">
        <Panel title="Weight-sorted catalog">
          <LatestRowsTable entries={weighted.slice(0, 80)} />
        </Panel>
      </div>
    </>
  );
}
