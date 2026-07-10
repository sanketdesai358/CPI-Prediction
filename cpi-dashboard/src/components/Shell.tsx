import type { ReactNode } from "react";

export function PageTitle({
  eyebrow,
  title,
  children
}: {
  eyebrow?: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="mb-5">
      {eyebrow ? <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-teal">{eyebrow}</div> : null}
      <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1>
      {children ? <div className="mt-2 max-w-3xl text-sm leading-6 text-muted">{children}</div> : null}
    </div>
  );
}

export function Panel({ title, children, className = "" }: { title?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded border border-line bg-white p-4 shadow-subtle ${className}`}>
      {title ? <h2 className="mb-3 text-base font-semibold">{title}</h2> : null}
      {children}
    </section>
  );
}

export function MetricCard({
  label,
  value,
  subvalue,
  tone = "neutral"
}: {
  label: string;
  value: string;
  subvalue?: string;
  tone?: "neutral" | "up" | "down";
}) {
  const toneClass = tone === "up" ? "text-rose" : tone === "down" ? "text-teal" : "text-ink";
  return (
    <div className="rounded border border-line bg-white p-4 shadow-subtle">
      <div className="text-xs font-medium uppercase tracking-wide text-muted">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${toneClass}`}>{value}</div>
      {subvalue ? <div className="mt-1 text-xs text-muted">{subvalue}</div> : null}
    </div>
  );
}
