import "server-only";

import { unstable_cache, revalidateTag } from "next/cache";
import registryJson from "@/data/registry.json";
import type { RegistryEntry } from "./types";

const BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/";
const LABSTAT_CURRENT_URL = "https://download.bls.gov/pub/time.series/cu/cu.data.0.Current";
const REGISTRY = registryJson as RegistryEntry[];

type BlsPoint = {
  seriesID: string;
  data: Array<{ year: string; period: string; value: string }>;
};

function userAgent(): string {
  return process.env.BLS_USER_AGENT ?? "CPI dashboard contact: cpi-dashboard@example.com";
}

function chunk<T>(items: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let index = 0; index < items.length; index += size) chunks.push(items.slice(index, index + size));
  return chunks;
}

export function registrySeries(): string[] {
  const ids = new Set<string>();
  for (const entry of REGISTRY) {
    if (entry.series_nsa) ids.add(entry.series_nsa);
    if (entry.series_sa) ids.add(entry.series_sa);
  }
  return [...ids].sort();
}

async function fetchBlsApiUncached(seriesIds: string[], startYear: number, endYear: number) {
  const batchSize = process.env.BLS_API_KEY ? 50 : 25;
  const series: BlsPoint[] = [];
  for (const batch of chunk(seriesIds, batchSize)) {
    const body: Record<string, unknown> = {
      seriesid: batch,
      startyear: String(startYear),
      endyear: String(endYear)
    };
    if (process.env.BLS_API_KEY) body.registrationkey = process.env.BLS_API_KEY;
    const response = await fetch(BLS_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", "User-Agent": userAgent() },
      body: JSON.stringify(body),
      next: { tags: ["cpi-data"], revalidate: 60 * 60 * 12 }
    });
    if (!response.ok) throw new Error(`BLS API ${response.status}`);
    const payload = await response.json();
    if (payload.status !== "REQUEST_SUCCEEDED") {
      throw new Error(`BLS API ${payload.status}: ${(payload.message ?? []).join("; ")}`);
    }
    series.push(...(payload.Results?.series ?? []));
  }
  return series;
}

export const fetchBlsApi = unstable_cache(fetchBlsApiUncached, ["bls-series"], {
  tags: ["cpi-data"],
  revalidate: 60 * 60 * 12
});

export async function fetchBulkCurrent() {
  const response = await fetch(LABSTAT_CURRENT_URL, {
    headers: { "User-Agent": userAgent() },
    next: { tags: ["cpi-data"], revalidate: 60 * 60 * 12 }
  });
  if (!response.ok) throw new Error(`LABSTAT current ${response.status}`);
  return response.text();
}

export async function revalidateCpiData() {
  revalidateTag("cpi-data");
}
