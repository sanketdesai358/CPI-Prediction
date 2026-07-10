import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const registryPath = path.join(root, "src", "data", "registry.json");
const outPath = path.join(root, "work", "bls-refresh-sample.json");
const registry = JSON.parse(await fs.readFile(registryPath, "utf8"));
const series = [
  ...new Set(
    registry
      .flatMap((entry) => [entry.series_nsa, entry.series_sa])
      .filter((seriesId) => typeof seriesId === "string" && seriesId.length > 0)
  )
].sort();

const endYear = new Date().getUTCFullYear();
const startYear = endYear - 6;
const batchSize = process.env.BLS_API_KEY ? 50 : 25;
const sample = series.slice(0, batchSize);
const body = {
  seriesid: sample,
  startyear: String(startYear),
  endyear: String(endYear)
};
if (process.env.BLS_API_KEY) body.registrationkey = process.env.BLS_API_KEY;

const response = await fetch("https://api.bls.gov/publicAPI/v2/timeseries/data/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "User-Agent": process.env.BLS_USER_AGENT ?? "CPI dashboard contact: cpi-dashboard@example.com"
  },
  body: JSON.stringify(body)
});
const payload = await response.json();
await fs.mkdir(path.dirname(outPath), { recursive: true });
await fs.writeFile(outPath, `${JSON.stringify(payload, null, 2)}\n`);
console.log(`Fetched ${sample.length} series for ${startYear}-${endYear}; wrote ${path.relative(root, outPath)}.`);
