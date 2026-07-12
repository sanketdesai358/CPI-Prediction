import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import {
  buildComponentTrends,
  calculateYoyPoints,
  filterComponentTrends,
  pointChange,
  selectDisplayTrends,
  sortComponentTrends,
  TREND_COMPONENTS
} from "../src/lib/component-trends.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));

function monthAdd(start, offset) {
  const [year, month] = start.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1 + offset, 1));
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}`;
}

function point(month, index) {
  return {
    month,
    nsaIndex: index,
    saIndex: null,
    saMm: null,
    nsaYoy: null,
    ri: null,
    contribution: null
  };
}

function makeHistory(count, start = "2010-01", base = 100) {
  return Array.from({ length: count }, (_, index) => point(monthAdd(start, index), base + index));
}

const shuffled = makeHistory(13).reverse();
const yoy = calculateYoyPoints(shuffled, 5);
assert.equal(yoy.length, 1, "YoY starts only after 12 prior index levels exist");
assert.equal(yoy[0].month, "2011-01", "YoY points are sorted chronologically before calculation");
assert.equal(Number(yoy[0].yoy?.toFixed(8)), Number(((112 / 100 - 1) * 100).toFixed(8)), "YoY uses index_t / index_t-12 - 1");

const longYoy = calculateYoyPoints(makeHistory(140), 5);
assert.equal(longYoy.length, 120, "YoY output is capped at the latest 120 months");
assert.equal(longYoy[0].month, "2011-09", "120-month window keeps the latest chronological observations");

const missingHistory = [...makeHistory(13), point("2011-02", null), point("2011-03", 115)];
const missing = calculateYoyPoints(missingHistory, 5);
assert.equal(missing.find((row) => row.month === "2011-02").yoy, null, "Missing index values stay null inside a valid YoY window");

const accelerationHistory = makeHistory(18, "2020-01", 100).map((row, index) => ({ ...row, nsaIndex: index < 12 ? 100 : 100 + (index - 11) * 2 }));
const accelerationPoints = calculateYoyPoints(accelerationHistory, 5);
assert.equal(Number(pointChange(accelerationPoints, 3)?.toFixed(8)), Number((accelerationPoints.at(-1).yoy - accelerationPoints.at(-4).yoy).toFixed(8)), "Three-month acceleration is latest YoY minus YoY three months earlier");

const dashboardCache = JSON.parse(readFileSync(join(__dirname, "..", "src", "data", "dashboard-cache.json"), "utf8"));
const trends = buildComponentTrends(dashboardCache.entries);
assert.equal(trends.length, TREND_COMPONENTS.length, "All configured trend components are built");
assert.equal(trends.filter((trend) => trend.missing).length, 0, "All requested series map to existing cached metadata");

const foodAtHome = trends.find((trend) => trend.itemCode === "SAF11");
const foodEntry = dashboardCache.entries.find((entry) => entry.itemCode === "SAF11");
assert.ok(foodAtHome && foodEntry, "Food at home exists in trend output and source cache");
assert.equal(foodAtHome.points.at(-1).month, foodEntry.latest.month, "Latest trend month matches source latest month");
assert.ok(Math.abs(foodAtHome.latestYoy - foodEntry.latest.nsaYoy * 100) < 1e-10, "Calculated YoY matches cached BLS-derived YoY");

const housing = filterComponentTrends(trends, { group: "Housing" });
assert.ok(housing.length > 0 && housing.every((trend) => trend.group === "Housing"), "Category filtering keeps only the requested group");
assert.ok(filterComponentTrends(trends, { search: "air" }).some((trend) => trend.itemCode === "SETG01"), "Search finds display names and official mapped series");

const byWeight = sortComponentTrends(trends, "weightDesc");
assert.ok((byWeight[0].currentRi ?? 0) >= (byWeight[1].currentRi ?? 0), "Weight sort is descending by default");
const byLatestAsc = sortComponentTrends(trends, "latestAsc");
assert.ok((byLatestAsc[0].latestYoy ?? Infinity) <= (byLatestAsc.at(-1).latestYoy ?? -Infinity), "Latest YoY ascending sort works");
const byAcceleration = sortComponentTrends(trends, "accelerationDesc");
assert.ok((byAcceleration[0].threeMonthChange ?? -Infinity) >= (byAcceleration[1].threeMonthChange ?? -Infinity), "Acceleration sort works");
assert.equal(selectDisplayTrends(trends, 10).length, 10, "Display-count selector can show 10 charts");
assert.equal(selectDisplayTrends(trends, 15).length, 15, "Display-count selector can show 15 charts");
assert.equal(selectDisplayTrends(trends, 20).length, 20, "Display-count selector can show 20 charts");

console.log("component trend tests passed");
