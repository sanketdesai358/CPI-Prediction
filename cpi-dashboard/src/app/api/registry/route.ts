import { NextResponse } from "next/server";
import { getRegistry } from "@/lib/data";

export const dynamic = "force-static";

export function GET() {
  return NextResponse.json({ registry: getRegistry() });
}
