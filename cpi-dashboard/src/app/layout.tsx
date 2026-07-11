import type { Metadata } from "next";
import Link from "next/link";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";
import { getDashboardData } from "@/lib/data";
import { formatMonth } from "@/lib/format";

export const metadata: Metadata = {
  title: "CPI Component Dashboard",
  description: "Component-level CPI-U dashboard powered by U.S. Bureau of Labor Statistics data."
};

const nav = [
  { href: "/forecast", label: "Forecast" },
  { href: "/", label: "Overview" },
  { href: "/components", label: "Components" },
  { href: "/challenger", label: "Challenger" },
  { href: "/heatmap", label: "Heatmap" },
  { href: "/contributions", label: "Contributions" },
  { href: "/methodology", label: "Methodology" }
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const data = getDashboardData();
  return (
    <html lang="en">
      <body>
        <header className="border-b border-line bg-white">
          <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
            <Link href="/" className="focus-ring rounded-sm">
              <div className="text-lg font-semibold tracking-tight">CPI Component Dashboard</div>
              <div className="text-xs text-muted">U.S. city average, CPI-U</div>
            </Link>
            <nav className="flex flex-wrap gap-2 text-sm">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="focus-ring rounded border border-line bg-wash px-3 py-1.5 hover:border-teal hover:text-teal"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        <footer className="mt-8 border-t border-line bg-white">
          <div className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-4 text-xs text-muted md:flex-row md:items-center md:justify-between">
            <span>
              Data as of {formatMonth(data.refMonth)}, released {data.releaseDate}. Source: U.S. Bureau of
              Labor Statistics.
            </span>
            <span>Generated {data.generatedAt}</span>
          </div>
        </footer>
        <Analytics />
      </body>
    </html>
  );
}
