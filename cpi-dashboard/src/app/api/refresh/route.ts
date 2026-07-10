import { NextRequest, NextResponse } from "next/server";
import { revalidateCpiData } from "@/lib/bls";
import calendar from "@/data/release-calendar.json";
import type { ReleaseCalendarEntry } from "@/lib/types";

export const dynamic = "force-dynamic";

function isReleaseDay(today: string, entries: ReleaseCalendarEntry[]) {
  return entries.some((entry) => entry.releaseDate === today);
}

export async function GET(request: NextRequest) {
  const mode = request.nextUrl.searchParams.get("mode") ?? "manual";
  const today = new Date().toISOString().slice(0, 10);
  const entries = calendar as ReleaseCalendarEntry[];
  const shouldRefresh = mode !== "release" || isReleaseDay(today, entries);
  if (shouldRefresh) {
    await revalidateCpiData();
  }
  return NextResponse.json({
    ok: true,
    mode,
    today,
    refreshed: shouldRefresh,
    message: shouldRefresh
      ? "CPI data cache tags were revalidated."
      : "Skipped because today is not a CPI release date in release-calendar.json."
  });
}
