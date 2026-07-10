import { NextResponse } from "next/server";
import { getBacktests, getForecast, getScore } from "@/lib/data";

export const dynamic = "force-static";

export function GET() {
  return NextResponse.json({
    forecast: getForecast(),
    score: getScore(),
    backtests: getBacktests(),
    storage: "checked-in JSON under src/data/forecast; replace with Vercel Blob/KV fetch for production uploads"
  });
}
