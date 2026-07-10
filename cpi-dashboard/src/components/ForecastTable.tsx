"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { ForecastComponentRow } from "@/lib/types";
import { formatPercent, formatPp, formatWeight } from "@/lib/format";

function groupFor(row: ForecastComponentRow) {
  const code = row.itemCode;
  if (code.startsWith("SEH") || code.startsWith("SAH")) return "Housing";
  if (code.startsWith("SEF") || code.startsWith("SAF") || code.startsWith("SSF")) return "Food";
  if (row.name.toLowerCase().includes("gasoline") || row.name.toLowerCase().includes("energy")) return "Energy";
  if (code.startsWith("SET")) return "Transportation";
  if (code.startsWith("SEM") || code.startsWith("SAM")) return "Medical care";
  return "Core other";
}

export function ForecastTable({ rows }: { rows: ForecastComponentRow[] }) {
  const [mode, setMode] = useState<"tier" | "group">("tier");
  const grouped = useMemo(() => {
    const map = new Map<string, ForecastComponentRow[]>();
    for (const row of rows) {
      const key = mode === "tier" ? `Tier ${row.tier ?? "n/a"}` : groupFor(row);
      map.set(key, [...(map.get(key) ?? []), row]);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [rows, mode]);
  return (
    <div>
      <div className="mb-3 flex gap-2">
        <button className={`rounded border px-3 py-1 text-sm ${mode === "tier" ? "border-teal bg-teal text-white" : "border-line"}`} onClick={() => setMode("tier")}>
          By tier
        </button>
        <button className={`rounded border px-3 py-1 text-sm ${mode === "group" ? "border-teal bg-teal text-white" : "border-line"}`} onClick={() => setMode("group")}>
          By major group
        </button>
      </div>
      <div className="space-y-5">
        {grouped.map(([group, groupRows]) => (
          <section key={group}>
            <h3 className="mb-2 text-sm font-semibold">{group}</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-line text-xs uppercase text-muted">
                  <tr>
                    <th className="py-2 pr-4">Component</th>
                    <th className="py-2 pr-4">Model</th>
                    <th className="py-2 pr-4">Weight</th>
                    <th className="py-2 pr-4">SA m/m</th>
                    <th className="py-2 pr-4">Contribution</th>
                    <th className="py-2 pr-4">Driver snapshot</th>
                  </tr>
                </thead>
                <tbody>
                  {groupRows.slice(0, 80).map((row) => (
                    <tr key={row.itemCode} className="border-b border-line/70 align-top">
                      <td className="max-w-[280px] py-2 pr-4">
                        <Link href={`/components/${row.itemCode}`} className="font-medium text-teal hover:underline">
                          {row.name}
                        </Link>
                        <div className="text-xs text-muted">{row.itemCode}</div>
                      </td>
                      <td className="max-w-[260px] py-2 pr-4 text-muted">{row.modelType}</td>
                      <td className="py-2 pr-4">{formatWeight(row.model_weight)}</td>
                      <td className="py-2 pr-4">{formatPercent(row.forecast_sa_mm)}</td>
                      <td className="py-2 pr-4">{formatPp(row.contribution_pp)}</td>
                      <td className="max-w-[320px] py-2 pr-4 text-muted">{row.driverSnapshot}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
