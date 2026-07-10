import Link from "next/link";
import type { ComponentEntry } from "@/lib/types";
import { componentHref } from "@/lib/data";
import { formatIndex, formatPercent, formatPp, formatWeight, signedClass } from "@/lib/format";

export function LatestRowsTable({ entries }: { entries: ComponentEntry[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase text-muted">
          <tr>
            <th className="py-2 pr-4">Component</th>
            <th className="py-2 pr-4">Weight</th>
            <th className="py-2 pr-4">SA m/m</th>
            <th className="py-2 pr-4">SA index</th>
            <th className="py-2 pr-4">Contribution</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.itemCode} className="border-b border-line/70">
              <td className="max-w-[360px] py-2 pr-4">
                <Link href={componentHref(entry.itemCode)} className="font-medium text-teal hover:underline">
                  {entry.name}
                </Link>
                <div className="text-xs text-muted">{entry.itemCode}</div>
              </td>
              <td className="py-2 pr-4">{formatWeight(entry.currentRi)}</td>
              <td className={`py-2 pr-4 ${signedClass(entry.latest.saMm)}`}>{formatPercent(entry.latest.saMm)}</td>
              <td className="py-2 pr-4">{formatIndex(entry.latest.saIndex)}</td>
              <td className={`py-2 pr-4 ${signedClass(entry.latest.contribution)}`}>
                {formatPp(entry.latest.contribution)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
