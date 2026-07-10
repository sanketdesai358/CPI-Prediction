import { notFound } from "next/navigation";
import { DetailChart } from "@/components/Charts";
import { LatestRowsTable } from "@/components/DataTable";
import { MetricCard, PageTitle, Panel } from "@/components/Shell";
import { getBacktests, getComponent, getDashboardData, getForecastComponent, getModelMeta } from "@/lib/data";
import { formatIndex, formatMonth, formatPercent, formatPp, formatWeight } from "@/lib/format";

export function generateStaticParams() {
  return getDashboardData().entries.map((entry) => ({ itemCode: entry.itemCode }));
}

export default async function ComponentDetailPage({ params }: { params: Promise<{ itemCode: string }> }) {
  const { itemCode } = await params;
  const component = getComponent(decodeURIComponent(itemCode));
  if (!component) notFound();
  const model = getModelMeta(component.itemCode);
  const forecastComponent = getForecastComponent(component.itemCode);
  const commodityModel = forecastComponent?.commodityModel;
  const backtest = getBacktests().C;
  const league = backtest.componentLeague.find((row) => row.itemCode === component.itemCode);
  const lastThree = component.history.slice(-3);
  const latestRows = lastThree.map((point) => ({ ...component, latest: point }));
  return (
    <>
      <PageTitle eyebrow={component.itemCode} title={component.name}>
        {component.formula} · {component.collection}
      </PageTitle>
      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard label="Current RI" value={formatWeight(component.currentRi)} subvalue={`Dec RI ${formatWeight(component.decRi)}`} />
        <MetricCard label="Latest SA m/m" value={formatPercent(component.latest.saMm)} subvalue={formatMonth(component.latest.month)} />
        <MetricCard label="Latest SA index" value={formatIndex(component.latest.saIndex)} subvalue={formatMonth(component.latest.month)} />
        <MetricCard label="Contribution" value={formatPp(component.latest.contribution)} subvalue="percentage points" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <Panel title="Time series">
          <DetailChart history={component.history} />
        </Panel>
        <div className="space-y-4">
          <Panel title="Methodology">
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="font-semibold">Formula</dt>
                <dd className="text-muted">{component.formula}</dd>
              </div>
              <div>
                <dt className="font-semibold">Collection</dt>
                <dd className="text-muted">{component.collection}</dd>
              </div>
              <div>
                <dt className="font-semibold">Quality adjustment / imputation</dt>
                <dd className="text-muted">{component.qaMethod || "BLS direct quality adjustment/imputation as applicable"}</dd>
              </div>
              <div>
                <dt className="font-semibold">Alternative data</dt>
                <dd className="text-muted">{component.altData || "None specified in the registry"}</dd>
              </div>
              <div>
                <dt className="font-semibold">BLS links</dt>
                <dd className="space-y-1">
                  {component.links.slice(0, 6).map((link) => (
                    <a key={link} href={link} className="block break-all text-teal hover:underline">
                      {link}
                    </a>
                  ))}
                </dd>
              </div>
            </dl>
          </Panel>
          <Panel title="Model">
            <dl className="space-y-3 text-sm">
              <div><dt className="font-semibold">Tier</dt><dd className="text-muted">{model?.tier ?? "not modeled"}</dd></div>
              <div><dt className="font-semibold">Model type</dt><dd className="text-muted">{model?.model_type ?? "n/a"}</dd></div>
              <div><dt className="font-semibold">Input series</dt><dd className="text-muted">{model?.input_series?.length ? model.input_series.join(", ") : "none / statistical fallback"}</dd></div>
              <div><dt className="font-semibold">Pass-through lags</dt><dd className="text-muted">{model?.pass_through_lags?.length ? model.pass_through_lags.join(", ") : "n/a"}</dd></div>
              <div><dt className="font-semibold">Backtest MAE vs benchmark</dt><dd className="text-muted">{league ? `${league.mae.toFixed(4)} vs ${league.benchmarkMae.toFixed(4)}` : "not yet scored in seeded backtest"}</dd></div>
            </dl>
          </Panel>
          {commodityModel ? (
            <Panel title="Commodity factor">
              <dl className="space-y-3 text-sm">
                <div><dt className="font-semibold">Complex</dt><dd className="text-muted">{commodityModel.complex}</dd></div>
                <div><dt className="font-semibold">Latent factor</dt><dd className="text-muted">{commodityModel.latentFactor}</dd></div>
                <div><dt className="font-semibold">Mapped cuts</dt><dd className="text-muted">{commodityModel.mappedCuts.join(", ")}</dd></div>
                <div><dt className="font-semibold">Fitted lag / loading</dt><dd className="text-muted">lag {commodityModel.selectedLag}, loading {commodityModel.estimatedLoading.toFixed(2)}</dd></div>
                <div><dt className="font-semibold">Validation</dt><dd className="text-muted">AP-CPI corr {commodityModel.validation.apCpiCorrelation === null ? "n/a" : commodityModel.validation.apCpiCorrelation.toFixed(2)}; wholesale-AP corr {commodityModel.validation.wholesaleApCorrelation === null ? "n/a" : commodityModel.validation.wholesaleApCorrelation.toFixed(2)}</dd></div>
                <div><dt className="font-semibold">Decision</dt><dd className="text-muted">{commodityModel.decision.replaceAll("_", " ")}</dd></div>
              </dl>
            </Panel>
          ) : null}
        </div>
      </div>

      <div className="mt-4">
        <Panel title="Last 3 months">
          <LatestRowsTable entries={latestRows} />
        </Panel>
      </div>
    </>
  );
}
