import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const modelRoot = process.env.CPI_MODEL_ROOT
  ? path.resolve(process.env.CPI_MODEL_ROOT)
  : path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/, "$1")), "..", "..", "..");
const workspaceRoot = path.dirname(modelRoot);
const defaultOutput = path.join(workspaceRoot, "cpi-model-archive", "Actual_vs_Predicted_June_2026.xlsx");
const outputPath = path.resolve(process.argv[2] || defaultOutput);

async function loadScores() {
  const runsDir = path.join(modelRoot, "runs");
  const entries = await fs.readdir(runsDir, { withFileTypes: true });
  const scores = [];
  for (const entry of entries) {
    if (!entry.isDirectory() || !/^\d{4}-\d{2}$/.test(entry.name)) continue;
    const scorePath = path.join(runsDir, entry.name, "score.json");
    try {
      const score = JSON.parse(await fs.readFile(scorePath, "utf8"));
      if (score.status === "scored" && score.headline && Array.isArray(score.rows)) scores.push(score);
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
    }
  }
  return scores.sort((a, b) => a.month.localeCompare(b.month));
}

const scores = await loadScores();
if (!scores.length) throw new Error("No scored release artifacts were found under cpi-model/runs.");

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Headline History");
const components = workbook.worksheets.add("Component Scores");
summary.showGridLines = false;
components.showGridLines = false;

const headlineHeaders = [
  "Forecast Month", "Series", "SA m/m Estimate", "SA m/m Actual", "SA Error (bp)",
  "NSA m/m Estimate", "NSA m/m Actual", "NSA Error (bp)", "SA y/y Estimate",
  "SA y/y Actual", "SA y/y Error (bp)", "NSA y/y Estimate", "NSA y/y Actual",
  "NSA y/y Error (bp)", "Components Scored", "Live Feeds", "Explicit Fallbacks",
];
const headlineRows = [];
for (const score of scores) {
  for (const [series, values] of [["Headline CPI", score.headline], ["Core CPI", score.core]]) {
    if (!values) continue;
    headlineRows.push([
      score.month, series, values.forecastSaMm ?? null, values.actualSaMm ?? null, null,
      values.forecastNsaMm ?? null, values.actualNsaMm ?? null, null,
      values.forecastSaYoy ?? null, values.actualSaYoy ?? null, null,
      values.forecastNsaYoy ?? null, values.actualNsaYoy ?? null, null,
      score.summary?.scoredComponentCount ?? score.rows.length,
      score.summary?.liveFeedCount ?? null,
      score.summary?.fallbackCount ?? null,
    ]);
  }
}

summary.getRange("A1:Q1").merge();
summary.getRange("A1").values = [["CPI Forecast vs Actual History"]];
summary.getRange("A2:Q2").merge();
summary.getRange("A2").values = [["Production estimates are the archived pre-release values. Errors are estimate minus actual; m/m and y/y rates are stored as numeric percentages."]];
summary.getRange("A4:Q4").values = [headlineHeaders];
summary.getRangeByIndexes(4, 0, headlineRows.length, headlineHeaders.length).values = headlineRows;
for (let row = 5; row < 5 + headlineRows.length; row += 1) {
  summary.getRange(`E${row}`).formulas = [[`=(C${row}-D${row})*10000`]];
  summary.getRange(`H${row}`).formulas = [[`=(F${row}-G${row})*10000`]];
  summary.getRange(`K${row}`).formulas = [[`=(I${row}-J${row})*10000`]];
  summary.getRange(`N${row}`).formulas = [[`=(L${row}-M${row})*10000`]];
}
const headlineEnd = 4 + headlineRows.length;
const headlineTable = summary.tables.add(`A4:Q${headlineEnd}`, true, "HeadlineHistoryTable");
headlineTable.style = "TableStyleMedium2";
summary.freezePanes.freezeRows(4);
summary.freezePanes.freezeColumns(2);

const componentHeaders = [
  "Forecast Month", "Item Code", "Component", "Tier", "Model Type", "RI Weight",
  "SA m/m Estimate", "SA m/m Actual", "SA Error (bp)", "NSA m/m Estimate",
  "NSA m/m Actual", "NSA Error (bp)", "Forecast SA Contribution", "Actual SA Contribution",
  "Contribution Error", "Feed Status", "Fallback Used", "Driver Snapshot",
];
const componentRows = [];
for (const score of scores) {
  for (const row of score.rows) {
    componentRows.push([
      score.month, row.itemCode, row.name, row.tier ?? null, row.modelType ?? null,
      row.weightRi == null ? null : row.weightRi / 100,
      row.forecastSaMm ?? null, row.actualSaMm ?? null, null,
      row.forecastNsaMm ?? null, row.actualNsaMm ?? null, null,
      row.forecastContributionPp ?? row.forecastContribution ?? null,
      row.actualContributionPp ?? row.actualContribution ?? null,
      null, row.feedStatus ?? "CPI-history model", Boolean(row.fallbackUsed), row.driverSnapshot ?? null,
    ]);
  }
}

components.getRange("A1:R1").merge();
components.getRange("A1").values = [["All Production Component Forecasts vs Actuals"]];
components.getRange("A2:R2").merge();
components.getRange("A2").values = [["One row per scored component and release month. Contribution columns are percentage points of headline CPI on an SA basis."]];
components.getRange("A4:R4").values = [componentHeaders];
components.getRangeByIndexes(4, 0, componentRows.length, componentHeaders.length).values = componentRows;
for (let row = 5; row < 5 + componentRows.length; row += 1) {
  components.getRange(`I${row}`).formulas = [[`=(G${row}-H${row})*10000`]];
  components.getRange(`L${row}`).formulas = [[`=(J${row}-K${row})*10000`]];
  components.getRange(`O${row}`).formulas = [[`=M${row}-N${row}`]];
}
const componentEnd = 4 + componentRows.length;
const componentTable = components.tables.add(`A4:R${componentEnd}`, true, "ComponentScoresTable");
componentTable.style = "TableStyleMedium2";
components.freezePanes.freezeRows(4);
components.freezePanes.freezeColumns(3);

for (const sheet of [summary, components]) {
  sheet.getRange("A1:R1").format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF", size: 16 },
    rowHeight: 28,
    verticalAlignment: "center",
  };
  sheet.getRange("A2:R2").format = {
    fill: "#E6F4F1",
    font: { color: "#40566B", italic: true },
    wrapText: true,
    rowHeight: 32,
    verticalAlignment: "center",
  };
  sheet.getRange("A4:R4").format = {
    fill: "#DCE8F2",
    font: { bold: true, color: "#172033" },
    wrapText: true,
    rowHeight: 34,
    verticalAlignment: "center",
  };
}

summary.getRange(`C5:D${headlineEnd}`).format.numberFormat = "0.000%";
summary.getRange(`F5:G${headlineEnd}`).format.numberFormat = "0.000%";
summary.getRange(`I5:J${headlineEnd}`).format.numberFormat = "0.000%";
summary.getRange(`L5:M${headlineEnd}`).format.numberFormat = "0.000%";
summary.getRange(`E5:E${headlineEnd}`).format.numberFormat = "0.0";
summary.getRange(`H5:H${headlineEnd}`).format.numberFormat = "0.0";
summary.getRange(`K5:K${headlineEnd}`).format.numberFormat = "0.0";
summary.getRange(`N5:N${headlineEnd}`).format.numberFormat = "0.0";

components.getRange(`F5:F${componentEnd}`).format.numberFormat = "0.000%";
components.getRange(`G5:H${componentEnd}`).format.numberFormat = "0.000%";
components.getRange(`J5:K${componentEnd}`).format.numberFormat = "0.000%";
components.getRange(`I5:I${componentEnd}`).format.numberFormat = "0.0";
components.getRange(`L5:L${componentEnd}`).format.numberFormat = "0.0";
components.getRange(`M5:O${componentEnd}`).format.numberFormat = '0.000 "pp"';
components.getRange(`Q5:Q${componentEnd}`).format.horizontalAlignment = "center";
components.getRange(`R5:R${componentEnd}`).format.wrapText = true;

summary.getRange("A:A").format.columnWidth = 14;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:N").format.columnWidth = 15;
summary.getRange("O:Q").format.columnWidth = 15;
components.getRange("A:A").format.columnWidth = 14;
components.getRange("B:B").format.columnWidth = 13;
components.getRange("C:C").format.columnWidth = 34;
components.getRange("D:D").format.columnWidth = 8;
components.getRange("E:E").format.columnWidth = 27;
components.getRange("F:O").format.columnWidth = 15;
components.getRange("P:P").format.columnWidth = 22;
components.getRange("Q:Q").format.columnWidth = 13;
components.getRange("R:R").format.columnWidth = 70;

summary.getRange(`E5:E${headlineEnd}`).conditionalFormats.add("colorScale", {
  colors: ["#0F766E", "#FFFFFF", "#B91C1C"], thresholds: ["min", { type: "num", value: 0 }, "max"],
});
components.getRange(`I5:I${componentEnd}`).conditionalFormats.add("colorScale", {
  colors: ["#0F766E", "#FFFFFF", "#B91C1C"], thresholds: ["min", { type: "num", value: 0 }, "max"],
});
components.getRange(`O5:O${componentEnd}`).conditionalFormats.add("colorScale", {
  colors: ["#0F766E", "#FFFFFF", "#B91C1C"], thresholds: ["min", { type: "num", value: 0 }, "max"],
});

const headlineCheck = await workbook.inspect({
  kind: "table",
  range: `Headline History!A4:Q${Math.min(headlineEnd, 10)}`,
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 17,
});
const componentCheck = await workbook.inspect({
  kind: "table",
  range: "Component Scores!A4:R10",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 18,
});
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(headlineCheck.ndjson);
console.log(componentCheck.ndjson);
console.log(formulaErrors.ndjson);

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const previewDir = process.env.CPI_WORKBOOK_PREVIEW_DIR
  ? path.resolve(process.env.CPI_WORKBOOK_PREVIEW_DIR)
  : path.join(process.cwd(), ".workbook-preview");
await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, fileName] of [
  ["Headline History", `A1:Q${Math.min(headlineEnd, 12)}`, "headline-history.png"],
  ["Component Scores", "A1:R18", "component-scores.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await preview.arrayBuffer()));
}
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });

console.log(JSON.stringify({ outputPath, scoredMonths: scores.map((score) => score.month), componentRows: componentRows.length, headlineRows: headlineRows.length }));
