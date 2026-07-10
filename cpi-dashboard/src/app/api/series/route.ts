import { NextRequest, NextResponse } from "next/server";
import { getComponent, getDashboardData } from "@/lib/data";

export const dynamic = "force-dynamic";

export function GET(request: NextRequest) {
  const itemCode = request.nextUrl.searchParams.get("itemCode");
  const data = getDashboardData();
  if (!itemCode) {
    return NextResponse.json({
      refMonth: data.refMonth,
      latestMonths: data.latestMonths,
      entries: data.entries.map((entry) => ({
        itemCode: entry.itemCode,
        name: entry.name,
        latest: entry.latest,
        currentRi: entry.currentRi
      }))
    });
  }
  const component = getComponent(itemCode);
  if (!component) {
    return NextResponse.json({ error: "Unknown itemCode" }, { status: 404 });
  }
  return NextResponse.json({
    refMonth: data.refMonth,
    component
  });
}
