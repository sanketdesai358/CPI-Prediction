import { ComponentTrendsDashboard } from "@/components/ComponentTrends";
import { PageTitle } from "@/components/Shell";
import { buildComponentTrends } from "@/lib/component-trends";
import { getDashboardData } from "@/lib/data";

export default function ComponentTrendsPage() {
  const data = getDashboardData();
  const trends = buildComponentTrends(data.entries);
  return (
    <>
      <PageTitle eyebrow="Trends" title="Major CPI Component Trends">
        Monthly year-over-year inflation across the largest CPI categories
      </PageTitle>
      <ComponentTrendsDashboard trends={trends} />
    </>
  );
}
