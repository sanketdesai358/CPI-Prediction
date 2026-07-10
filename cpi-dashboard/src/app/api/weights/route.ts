import { NextResponse } from "next/server";
import { getDashboardData } from "@/lib/data";

export const dynamic = "force-static";

export function GET() {
  const data = getDashboardData();
  return NextResponse.json({
    refMonth: data.refMonth,
    weightVintage: data.weightVintage,
    decemberMonth: data.decemberMonth,
    weights: data.entries.map((entry) => ({
      itemCode: entry.itemCode,
      name: entry.name,
      decRi: entry.decRi,
      currentRi: entry.currentRi
    }))
  });
}
