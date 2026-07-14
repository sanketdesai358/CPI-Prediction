import Link from "next/link";

const tabs = [
  { href: "/forecast", label: "Current Forecast", key: "forecast" },
  { href: "/forecast/model-divergence", label: "Model Divergence", key: "model-divergence" }
] as const;

export function ForecastNav({ active }: { active: "forecast" | "track" | "model-divergence" }) {
  return (
    <div className="mb-4 flex flex-wrap gap-2">
      {tabs.map((tab) => (
        <Link
          key={tab.key}
          href={tab.href}
          className={`rounded border px-3 py-2 text-sm font-medium ${
            active === tab.key ? "border-teal bg-teal text-white" : "border-line bg-white text-ink hover:border-teal"
          }`}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
}
