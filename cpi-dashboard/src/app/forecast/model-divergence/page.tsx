import { ForecastModelDivergence } from "@/components/ForecastModelDivergence";
import { ForecastNav } from "@/components/ForecastNav";
import { PageTitle, Panel } from "@/components/Shell";
import { getChallenger, getDashboardData, getForecast } from "@/lib/data";
import { formatMonth } from "@/lib/format";
import type { ChallengerResult } from "@/lib/types";

const forecastDivergenceMajorCodes = new Set(["SAF1", "SA0E", "SAH1", "SETA02", "SAT1", "SAM", "SAR", "SAE", "SAG"]);

function filterChallengerForForecastDivergence(challenger: ChallengerResult | null): ChallengerResult | null {
  if (!challenger) return null;
  return {
    ...challenger,
    currentForecast: challenger.currentForecast
      ? {
          ...challenger.currentForecast,
          majorRows: challenger.currentForecast.majorRows?.filter((row) => forecastDivergenceMajorCodes.has(row.series))
        }
      : null,
    majorComponentDiagnostics: challenger.majorComponentDiagnostics?.filter((row) => forecastDivergenceMajorCodes.has(row.itemCode)),
    majorComponentSeries: Object.fromEntries(
      Object.entries(challenger.majorComponentSeries ?? {}).filter(([code]) => forecastDivergenceMajorCodes.has(code))
    )
  };
}

export default function ForecastModelDivergencePage() {
  const forecast = getForecast();
  const challenger = getChallenger();
  const data = getDashboardData();
  if (!forecast) {
    return (
      <>
        <PageTitle eyebrow="Forecast" title="Model Divergence">
          Compare your production model against challenger forecasts.
        </PageTitle>
        <ForecastNav active="model-divergence" />
        <Panel title="No forecast uploaded">
          <p className="text-sm text-muted">Upload a production forecast run to populate this page.</p>
        </Panel>
      </>
    );
  }
  return (
    <>
      <PageTitle eyebrow="Forecast" title="Model Divergence">
        Your production model for {formatMonth(forecast.forecastMonth)} compared with HRNN, I-GRU, Seasonal AR, and fallback baselines.
      </PageTitle>
      <ForecastNav active="model-divergence" />
      <ForecastModelDivergence
        forecast={forecast}
        challenger={filterChallengerForForecastDivergence(challenger)}
        entries={data.entries.filter((entry) => forecastDivergenceMajorCodes.has(entry.itemCode) || !["SACL1E", "SASLE"].includes(entry.itemCode))}
      />
      <div className="mt-4 text-xs text-muted">
        Current production values are from the production forecast artifact. Historical production replay is only shown where a true walk-forward artifact exists.
      </div>
    </>
  );
}
