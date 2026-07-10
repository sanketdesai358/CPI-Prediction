import fs from "node:fs/promises";
import path from "node:path";

const url = "https://www.bls.gov/schedule/news_release/cpi.htm";
const root = path.resolve(import.meta.dirname, "..");
const output = path.join(root, "src", "data", "release-calendar.json");

const response = await fetch(url, {
  headers: {
    "User-Agent": process.env.BLS_USER_AGENT ?? "CPI dashboard contact: cpi-dashboard@example.com"
  }
});

if (!response.ok) {
  throw new Error(`BLS release calendar ${response.status}`);
}

const html = await response.text();
const entries = [];
const rowRegex = /<tr[^>]*>\s*<td>(.*?)<\/td>\s*<td>(.*?)<\/td>\s*<td>(.*?)<\/td>\s*<\/tr>/g;
const months = new Map(
  [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
  ].map((month, index) => [month, index])
);
for (const [abbr, index] of [
  ["Jan", 0],
  ["Feb", 1],
  ["Mar", 2],
  ["Apr", 3],
  ["Jun", 5],
  ["Jul", 6],
  ["Aug", 7],
  ["Sep", 8],
  ["Oct", 9],
  ["Nov", 10],
  ["Dec", 11]
]) {
  months.set(abbr, index);
}

for (const match of html.matchAll(rowRegex)) {
  const [, referenceMonth, releaseDateText, releaseTime] = match.map((value) =>
    value.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim()
  );
  const dateMatch = releaseDateText.match(/^([A-Z][a-z]+)\.?\s+(\d{1,2}),\s+(\d{4})$/);
  if (!dateMatch) continue;
  const [, month, day, year] = dateMatch;
  const date = new Date(Date.UTC(Number(year), months.get(month), Number(day)));
  if (Number.isNaN(date.valueOf())) continue;
  entries.push({
    releaseDate: date.toISOString().slice(0, 10),
    releaseTime: releaseTime.replace(/\s+/g, " ").trim(),
    text: `Consumer Price Index: ${referenceMonth}`
  });
}

const unique = [...new Map(entries.map((entry) => [entry.releaseDate, entry])).values()].sort((a, b) =>
  a.releaseDate.localeCompare(b.releaseDate)
);

await fs.writeFile(output, `${JSON.stringify(unique, null, 2)}\n`);
console.log(`Wrote ${path.relative(root, output)} with ${unique.length} entries.`);
