import { HeatmapGrid } from "@/components/Charts";
import { PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, getForecast, sortByWeight } from "@/lib/data";
import { formatMonth } from "@/lib/format";

export default function HeatmapPage() {
  const data = getDashboardData();
  const forecast = getForecast();
  const rows = sortByWeight(data.entries.filter((entry) => entry.formula !== "aggregate" && (entry.currentRi ?? 0) > 0));
  const hasProjection = Boolean(forecast?.forecastMonth && !data.heatmapMonths.includes(forecast.forecastMonth));
  return (
    <>
      <PageTitle eyebrow="Heatmap" title="Component momentum across the last 24 months">
        Cells show BLS seasonally adjusted m/m where published; otherwise they use a derived seasonal proxy from
        the component NSA index. Rows are sortable by the sticky columns or any month.
        Latest published month: {formatMonth(data.refMonth)}
        {hasProjection && forecast ? `; projection column: ${formatMonth(forecast.forecastMonth)}.` : "."}
      </PageTitle>
      <Panel>
        <HeatmapGrid entries={rows} months={data.heatmapMonths} forecast={forecast} />
      </Panel>
    </>
  );
}
