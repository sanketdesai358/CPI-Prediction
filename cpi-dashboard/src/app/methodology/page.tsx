import Link from "next/link";
import { PageTitle, Panel } from "@/components/Shell";
import { getDashboardData, getMethodologyRows } from "@/lib/data";
import { formatMonth } from "@/lib/format";

const layerRows = [
  ["Lower level, most strata", "Weighted geometric mean", "Quote relatives inside basic item-area cells"],
  ["Lower level exceptions", "Modified Laspeyres", "Selected shelter services, utilities, government fees, and medical services"],
  ["Shelter rent/OER", "Six-month chained relative", "Six rotating housing panels with age-bias adjustment"],
  ["Upper level CPI-U/CPI-W", "Lowe fixed-weight aggregation", "CE weights updated each January"],
  ["Seasonal adjustment", "X-13ARIMA-SEATS", "February factor refresh with five years revised"]
];

const externalPredictors = [
  ["Gasoline", "EIA weekly retail, OPIS/AAA daily, RBOB futures and crack spreads"],
  ["Rent/OER", "ZORI, Apartment List, BLS-Cleveland Fed New Tenant Rent Index, vacancies"],
  ["Used vehicles", "Manheim UVVI and Black Book"],
  ["New vehicles", "J.D. Power PIN, incentives, inventory and days-supply"],
  ["Airfares", "ARC ticketing data and jet fuel"],
  ["Food at home", "USDA, livestock/grain futures, scanner data"],
  ["Wireless/tech", "Carrier plan-offer scrapes and launch calendars"]
];

export default function MethodologyPage() {
  const data = getDashboardData();
  const rows = getMethodologyRows().slice(0, 220);
  return (
    <>
      <PageTitle eyebrow="Methodology" title="Registry, formulas, weights, and model hooks">
        The app uses the same validated registry as the Excel deliverable. Current data reference month is{" "}
        {formatMonth(data.refMonth)}; CE weight vintage is {data.weightVintage ?? "n/a"}.
      </PageTitle>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Calculation layers">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr>
                  <th className="py-2 pr-4">Layer</th>
                  <th className="py-2 pr-4">Method</th>
                  <th className="py-2 pr-4">Operational note</th>
                </tr>
              </thead>
              <tbody>
                {layerRows.map((row) => (
                  <tr key={row[0]} className="border-b border-line/70">
                    <td className="py-2 pr-4 font-medium">{row[0]}</td>
                    <td className="py-2 pr-4">{row[1]}</td>
                    <td className="py-2 pr-4 text-muted">{row[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
        <Panel title="Weight and contribution formulas">
          <div className="space-y-3 text-sm text-muted">
            <p>
              Relative importance is price-updated from the December RI base: RI(i,m) = 100 x [RI(i,Dec) x
              I(i,m)/I(i,Dec)] / [100 x I(all,m)/I(all,Dec)].
            </p>
            <p>
              Contribution to all-items m/m is approximated as prior-month RI x the component index relative.
              The contributions page displays the residual to the published headline.
            </p>
            <a className="text-teal hover:underline" href="https://www.bls.gov/cpi/tables/relative-importance/">
              BLS relative importance and weight information
            </a>
          </div>
        </Panel>
      </div>

      <div className="mt-4">
        <Panel title="External predictor map">
          <div className="grid gap-2 md:grid-cols-2">
            {externalPredictors.map(([component, predictors]) => (
              <div key={component} className="rounded border border-line p-3">
                <div className="font-medium">{component}</div>
                <div className="mt-1 text-sm text-muted">{predictors}</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="mt-4">
        <Panel title="Component methodology catalog">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr>
                  <th className="py-2 pr-4">Component</th>
                  <th className="py-2 pr-4">Formula</th>
                  <th className="py-2 pr-4">Collection</th>
                  <th className="py-2 pr-4">QA / imputation</th>
                  <th className="py-2 pr-4">Alt data</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((entry) => (
                  <tr key={entry.itemCode} className="border-b border-line/70 align-top">
                    <td className="max-w-[260px] py-2 pr-4">
                      <Link href={`/components/${entry.itemCode}`} className="font-medium text-teal hover:underline">
                        {entry.name}
                      </Link>
                      <div className="text-xs text-muted">{entry.itemCode}</div>
                    </td>
                    <td className="py-2 pr-4">{entry.formula}</td>
                    <td className="max-w-[340px] py-2 pr-4 text-muted">{entry.collection}</td>
                    <td className="max-w-[380px] py-2 pr-4 text-muted">{entry.qaMethod}</td>
                    <td className="max-w-[260px] py-2 pr-4 text-muted">{entry.altData || "none"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </>
  );
}
