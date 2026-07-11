from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cpi_model.costar_adr import (
    feed_payload,
    load_releases,
    lodging_forecast,
    revision_statistics,
    seasonal_ar_fallback,
    walk_forward_backtest,
)
from cpi_model.data import entry_by_code


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.3f}%"


def main() -> None:
    releases = load_releases()
    feed = feed_payload()
    forecast = lodging_forecast("2026-06", feed)
    old_stratum = seasonal_ar_fallback("2026-06")
    old_production = seasonal_ar_fallback("2026-06", code="SEHB")
    backtest = walk_forward_backtest(releases)
    revision = revision_statistics(releases)
    lodging_weight = float(entry_by_code()["SEHB"].get("currentRi") or 0.0)
    difference = None if not forecast or old_production is None else forecast["forecastNsaMm"] - old_production
    payload = {
        "source": "CoStar/STR public U.S. hotel press releases",
        "parsedReleases": len(releases),
        "weeklyReleases": sum(row.cadence == "weekly" for row in releases),
        "monthlyReleases": sum(row.cadence == "monthly" for row in releases),
        "publicationSpan": feed["truePublicationSpan"],
        "officialMonthSpan": {
            "start": min(row.month for row in releases if row.month),
            "end": max(row.month for row in releases if row.month),
        },
        "revision": revision,
        "backtest": backtest,
        "june2026": {
            "adrPrimaryNsaMm": forecast["forecastNsaMm"] if forecast else None,
            "seasonalArProductionNsaMm": old_production,
            "seasonalArHotelsMotelsNsaMm": old_stratum,
            "difference": difference,
            "headlineContributionDifferencePp": None if difference is None else lodging_weight * difference,
            "driver": forecast["driver"] if forecast else None,
            "model": forecast["model"] if forecast else None,
            "weeklyPrints": forecast["monthlyNowcast"]["weeklyPrints"] if forecast else [],
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    common = backtest["seasonalArCommon"]
    new = backtest["adrPrimary"]
    lines = [
        "# CoStar/STR ADR lodging model",
        "",
        f"Public cache span: {feed['truePublicationSpan']['start']} to {feed['truePublicationSpan']['end']}; "
        f"{payload['weeklyReleases']} weekly and {payload['monthlyReleases']} monthly releases parsed.",
        "",
        "## Window C walk-forward (common available span)",
        "",
        "| Model | Months | MAE | RMSE |",
        "|---|---:|---:|---:|",
        f"| CoStar ADR primary | {new['months']} | {pct(new['mae'])} | {pct(new['rmse'])} |",
        f"| Old Seasonal AR | {common['months']} | {pct(common['mae'])} | {pct(common['rmse'])} |",
        "",
        "## June 2026",
        "",
        f"- CoStar ADR primary lodging NSA m/m: {pct(payload['june2026']['adrPrimaryNsaMm'])}",
        f"- Old production Seasonal AR (`SEHB`) NSA m/m: {pct(old_production)}",
        f"- Narrow hotels/motels Seasonal AR (`SEHB02`) NSA m/m: {pct(old_stratum)}",
        f"- Headline contribution difference: {payload['june2026']['headlineContributionDifferencePp']:+.3f} pp",
        f"- Driver: {payload['june2026']['driver']}",
        "",
        "June actual remains pending until the July 14, 2026 CPI release and should then be scored through the archive scorer.",
        "",
        "## Honesty notes",
        "",
        "- Direct scripted requests currently receive HTTP 403; the feed uses cached public browser-rendered releases and reports refresh failures in feed health.",
        "- The public listing exposes unique parsed publications from March 2022 onward and official monthly levels from October 2023 onward. Older advertised filter years are not claimed as recovered.",
        "- ADR is a mix-weighted average room revenue measure; CPI holds room specifications more nearly fixed. A low fitted beta is therefore plausible.",
        "- Official monthly ADR is used for training when published; weekly day-weighted ADR is used for the unpublished current month.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'results.json'}")
    print(f"Wrote {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
