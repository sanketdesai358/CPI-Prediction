export type SeriesPoint = {
  month: string;
  nsaIndex: number | null;
  saIndex: number | null;
  saMm: number | null;
  nsaYoy: number | null;
  ri: number | null;
  contribution: number | null;
  saMethod?: "official" | "derived_nsa_seasonal_proxy" | "none";
};

export type RegistryEntry = {
  name: string;
  item_code: string;
  series_nsa: string;
  series_sa: string | null;
  parent: string | null;
  level: number;
  display_level: number;
  is_item_stratum: boolean;
  formula: string;
  collection: string;
  qa_method: string;
  alt_data: string;
  links: string[];
  notes: string;
};

export type ComponentEntry = {
  itemCode: string;
  name: string;
  parent: string | null;
  level: number;
  displayLevel: number;
  isItemStratum: boolean;
  formula: string;
  collection: string;
  qaMethod: string;
  altData: string;
  notes: string;
  links: string[];
  seriesNsa: string;
  seriesSa: string | null;
  saMethod?: "official" | "derived_nsa_seasonal_proxy" | "none";
  decRi: number | null;
  currentRi: number | null;
  weightVintage: number | null;
  decemberMonth: string | null;
  latest: SeriesPoint;
  history: SeriesPoint[];
};

export type WeightVintage = {
  weightVintage: number | null;
  decemberMonth: string | null;
  refMonth: string;
};

export type ContributionRow = {
  itemCode: string;
  name: string;
  contribution: number | null;
  currentRi: number | null;
  saMm: number | null;
};

export type ReleaseCalendarEntry = {
  releaseDate: string;
  releaseTime: string;
  text: string;
};

export type DashboardCache = {
  generatedAt: string;
  refMonth: string;
  latestMonths: string[];
  historyMonths: string[];
  heatmapMonths: string[];
  releaseDate: string;
  nextRelease: ReleaseCalendarEntry;
  source: string;
  weightVintage: number | null;
  decemberMonth: string | null;
  headline: {
    itemCode: "SA0";
    saMm: number | null;
    nsaYoy: number | null;
    saIndex: number | null;
    nsaIndex: number | null;
  };
  core: {
    itemCode: "SA0L1E";
    saMm: number | null;
    nsaYoy: number | null;
    saIndex: number | null;
    nsaIndex: number | null;
  };
  topContributors: ContributionRow[];
  entries: ComponentEntry[];
};

export type ForecastComponentRow = {
  itemCode: string;
  name: string;
  tier: number | null;
  modelType: string;
  model_weight: number;
  blsCurrentRi: number | null;
  forecast_nsa_mm: number;
  forecast_sa_mm: number;
  is_core: boolean;
  driverSnapshot: string;
  inputSeries: string[];
  passThroughLags: number[];
  eventCalendar: string[];
  sigma: number;
  component_yoy: number | null;
  contribution_pp: number;
  feedStatus?: FeedHealthComponent;
  commodityModel?: {
    complex: string;
    latentFactor: string;
    mappedCuts: string[];
    selectedLag: number;
    estimatedLoading: number;
    lagCorrelation: number | null;
    liveCutAdjustment: number;
    validation: {
      validator: string | null;
      wholesaleApCorrelation: number | null;
      apCpiCorrelation: number | null;
      note: string;
    };
    decision: string;
    notes: string;
  } | null;
};

export type FeedObservation = {
  date: string;
  value: number;
  label: string;
};

export type FeedHealthComponent = {
  itemCode: string;
  name: string;
  tier: number;
  primaryFeed: string;
  secondaryFeeds: string[];
  status: string;
  fallbackUsed: boolean;
  lastObservationDate: string | null;
  latestValue: number | null;
  unit: string;
  observationsUsed: FeedObservation[];
  details: string | null;
};

export type FeedHealth = {
  forecastMonth: string;
  generatedAt: string;
  summary: {
    componentsTracked: number;
    live: number;
    partial: number;
    fallbackOrBlocked: number;
    forecastErrors?: number;
  };
  components: FeedHealthComponent[];
  forecastErrors?: Array<{
    itemCode: string;
    name: string;
    stage: string;
    errorType: string;
    message: string;
  }>;
};

export type ForecastProjectionRow = {
  itemCode: string;
  name: string;
  parent?: string | null;
  weight: number | null;
  forecast_nsa_mm: number;
  forecast_sa_mm: number;
  contribution_pp: number;
  projectionSource: "model" | "AR fallback" | "parent" | "aggregate";
  projectionSourceDetail: string;
  childProjectionCount: number;
  displayInHeatmap: boolean;
};

export type ForecastRun = {
  forecastMonth: string;
  generatedAt: string;
  dataThrough: string;
  source: string;
  headline: {
    nsaMm: number;
    saMm: number;
    nsaYoy: number | null;
    saYoy?: number | null;
    saInterval: { p10: number; p50: number; p90: number };
  };
  core: {
    nsaMm: number;
    saMm: number;
    nsaYoy: number | null;
    saYoy?: number | null;
    saInterval: { p10: number; p50: number; p90: number };
  };
  baseEffects: Array<{ month: string; scenario_mm: number; headline_yoy: number | null }>;
  feedHealth?: FeedHealth["summary"];
  foodForwardPath?: {
    status: string;
    source: string;
    note: string;
    horizons: Array<{
      horizon: number;
      label: string;
      foodNsaMm: number;
      headlineContributionPp: number;
      interval: { p10: number; p50: number; p90: number };
      components: Array<{
        itemCode: string;
        name: string;
        nsaMm: number;
        contributionPp: number;
        interval: { p10: number; p50: number; p90: number };
        futuresFeaturesKept: boolean;
      }>;
    }>;
    lagReport?: {
      status: string;
      notes: string;
      rows: Array<{
        component: string;
        features: string[];
        availableFeatures: string[];
        kept: boolean;
        decision: string;
        expectedLagPeak: string;
        lagProfile: Array<{ lag: number; weight: number | null }>;
        windowC: { withoutFuturesMae: number | null; withFuturesMae: number | null; winner: string };
      }>;
    };
  };
  components: ForecastComponentRow[];
  projectionComponents?: ForecastProjectionRow[];
};

export type ScoreRow = {
  itemCode: string;
  name: string;
  forecastContribution: number | null;
  actualContribution: number | null;
  missPp: number | null;
};

export type ScoreResult = {
  month: string;
  status: string;
  headline?: {
    forecastNsaMm: number | null;
    actualNsaMm: number | null;
    forecastSaMm: number | null;
    actualSaMm: number | null;
    missSaPp: number | null;
  };
  rows: ScoreRow[];
};

export type BacktestResult = {
  window: string;
  requestedStart: string;
  availableStart: string | null;
  availableEnd: string | null;
  metrics: Record<string, number | null>;
  rolling24: Array<{ month: string; mae24: number | null }>;
  componentLeague: Array<{ itemCode: string; name: string; mae: number; benchmarkMae: number; note?: string }>;
  commodityComplex?: {
    window: string;
    requestedStart: string;
    notes: string;
    rows: Array<{
      itemCode: string;
      name: string;
      complex: string;
      mappedCuts: string[];
      withoutGranularMae: number | null;
      withGranularMae: number | null;
      winner: string;
      kept: boolean;
      validation: {
        validator: string | null;
        wholesaleApCorrelation: number | null;
        apCpiCorrelation: number | null;
        note: string;
      };
    }>;
  };
  rows: Array<Record<string, number | string | null>>;
  benchmarks: string[];
  diagnostics: Record<string, string>;
};

export type ChallengerVariant = "production" | "productionTier1" | "productionTier3" | "hrnn" | "iGru" | "seasonalAr";

export type ChallengerWindow = {
  requestedStart: string;
  availableStart: string | null;
  availableEnd: string | null;
  metrics: Record<string, number | null>;
  rolling24: Array<{ month: string; production: number | null; productionTier1?: number | null; productionTier3?: number | null; hrnn: number | null; iGru: number | null; seasonalAr: number | null }>;
};

export type ComponentComparisonRow = {
  itemCode: string;
  name: string;
  level: number | null;
  weight: number;
  productionMae: number | null;
  hrnnMae: number | null;
  iGruMae: number | null;
  seasonalArMae: number | null;
  bestModel: string;
  bestChallenger: string;
  verdict: "PRODUCTION WINS" | "HRNN WINS" | "I-GRU WINS" | "SEASONAL AR WINS" | "TIE";
  weightedGap: number;
  windowBHrnnGap: number | null;
};

export type ChallengerMeasureSet = {
  nsaMm: number | null;
  saMm: number | null;
  nsaYoy: number | null;
  saYoy: number | null;
};

export type ChallengerCurrentForecast = {
  forecastMonth: string;
  dataThrough: string;
  source: string;
  rows: Array<{
    series: string;
    label: string;
    weight?: number | null;
    actual: ChallengerMeasureSet;
    production: ChallengerMeasureSet;
    productionTier1?: ChallengerMeasureSet;
    productionTier3?: ChallengerMeasureSet;
    hrnn: ChallengerMeasureSet;
    iGru: ChallengerMeasureSet;
    seasonalAr: ChallengerMeasureSet;
  }>;
  componentRows?: Array<{
    series: string;
    label: string;
    weight?: number | null;
    modelType?: string | null;
    tier?: number | null;
    driverSnapshot?: string | null;
    actual: ChallengerMeasureSet;
    production: ChallengerMeasureSet;
    productionTier1?: ChallengerMeasureSet;
    productionTier3?: ChallengerMeasureSet;
    hrnn: ChallengerMeasureSet;
    iGru: ChallengerMeasureSet;
    seasonalAr: ChallengerMeasureSet;
  }>;
  majorRows?: Array<{
    series: string;
    label: string;
    weight?: number | null;
    actual: ChallengerMeasureSet;
    production: ChallengerMeasureSet;
    productionTier1?: ChallengerMeasureSet;
    productionTier3?: ChallengerMeasureSet;
    hrnn: ChallengerMeasureSet;
    iGru: ChallengerMeasureSet;
    seasonalAr: ChallengerMeasureSet;
  }>;
};

export type ChallengerMajorComponentRow = {
  itemCode: string;
  name: string;
  weight: number | null;
  latestActualMonth: string;
  latestActual: Pick<ChallengerMeasureSet, "saMm" | "nsaMm">;
  latestPrediction: Record<string, Pick<ChallengerMeasureSet, "saMm" | "nsaMm">>;
  latestError: Record<string, Pick<ChallengerMeasureSet, "saMm" | "nsaMm">>;
  windowC: Record<string, { saMmMae: number | null; nsaMmMae: number | null }>;
};

export type ChallengerMajorComponentSeriesRow = {
  month: string;
  actualNsaMm: number | null;
  actualSaMm: number | null;
} & Record<string, number | string | null>;

export type ChallengerSeriesRow = {
  month: string;
  actualNsaMm: number | null;
  actualSaMm: number | null;
  productionNsaMm: number | null;
  hrnnNsaMm: number | null;
  iGruNsaMm: number | null;
  seasonalArNsaMm: number | null;
};

export type ChallengerResult = {
  generatedAt: string;
  status: string;
  implementationStatus: string;
  source: string;
  variantLabels: Record<ChallengerVariant, string>;
  windows: Record<"A" | "B" | "C", ChallengerWindow>;
  currentForecast: ChallengerCurrentForecast | null;
  productionBacktestMetrics: Record<string, Record<string, number | null>>;
  rows: Array<Record<string, number | string | null>>;
  componentLeague: ComponentComparisonRow[];
  componentSeries: Record<string, ChallengerSeriesRow[]>;
  majorComponentSeries?: Record<string, ChallengerMajorComponentSeriesRow[]>;
  majorComponentDiagnostics?: ChallengerMajorComponentRow[];
  hierarchyLevelMetrics: Array<{
    level: number;
    components: number;
    hrnnMae: number | null;
    seasonalArMae: number | null;
    normalizedVsSeasonalAr: number | null;
  }>;
  adoptionCandidates: Array<{ itemCode: string; name: string; evidence: string }>;
  honestNotes: string[];
  runtime: { seconds: number; checkpointReuse: string };
};

export type ModelComparisonModelKey = "productionTier1" | "productionTier3" | "hrnn" | "iGru" | "seasonalAr";

export type ModelComparisonRow = {
  month: string;
  actualSaMm: number | null;
  actualNsaMm: number | null;
  actualSaYoy: number | null;
  actualNsaYoy: number | null;
} & Record<string, number | string | null>;

export type ModelComparisonSummaryRow = {
  model: ModelComparisonModelKey;
  label: string;
  start: string | null;
  end: string | null;
  months: number;
  fullSaMmMae?: number | null;
  fullSaMmRmse?: number | null;
  fullNsaMmMae?: number | null;
  fullNsaMmRmse?: number | null;
  fullSaYoyMae?: number | null;
  fullSaYoyRmse?: number | null;
  fullNsaYoyMae?: number | null;
  fullNsaYoyRmse?: number | null;
  commonSaMmMae?: number | null;
  commonSaMmRmse?: number | null;
  commonNsaMmMae?: number | null;
  commonNsaMmRmse?: number | null;
  commonSaYoyMae?: number | null;
  commonSaYoyRmse?: number | null;
  commonNsaYoyMae?: number | null;
  commonNsaYoyRmse?: number | null;
};

export type ModelComparisonResult = {
  source: string;
  commonStart: string;
  yoyConvention: string;
  models: Partial<Record<ModelComparisonModelKey, { label: string; color: string }>>;
  summary: ModelComparisonSummaryRow[];
  notes: string[];
  rows: ModelComparisonRow[];
};
