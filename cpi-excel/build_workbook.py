from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

import pandas as pd

from cpi_excel.constants import BASE_URLS, REGISTRY_FILENAME, WORKBOOK_FILENAME
from cpi_excel.data import fetch_series_data, latest_common_months, month_display, records_to_wide
from cpi_excel.labstat import build_registry, load_items, load_series, validate_registry, write_registry
from cpi_excel.ri import load_current_relative_importance
from cpi_excel.sources import download_text, next_cpi_release, parse_release_calendar
from cpi_excel.workbook import build_workbook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the CPI component workbook.")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore cached raw JSON/flat files and re-fetch from BLS.",
    )
    parser.add_argument(
        "--output",
        default=WORKBOOK_FILENAME,
        help=f"Workbook output path, default {WORKBOOK_FILENAME}.",
    )
    return parser.parse_args()


def release_summary(force: bool) -> str:
    try:
        html = download_text(
            BASE_URLS["release_calendar"],
            Path("data/raw/release-calendar-cpi.html"),
            force=force,
            timeout=60,
        )
        entries = parse_release_calendar(html)
        entry = next_cpi_release(entries)
        if entry:
            return f"{entry.release_date.isoformat()} {entry.release_time}"
    except Exception as exc:  # pragma: no cover - noncritical source-page parsing
        return f"See BLS release calendar ({exc})"
    return "See BLS release calendar"


def main() -> None:
    args = parse_args()
    force = bool(args.force_refresh)

    print("Loading BLS LABSTAT metadata...")
    items_df = load_items(force=force)
    series_df = load_series(force=force)

    print("Building and validating registry...")
    registry = build_registry(items_df, series_df)
    errors = validate_registry(registry, items_df, series_df)
    if errors:
        report = "\n".join(errors[:100])
        raise SystemExit(f"Registry validation failed with {len(errors)} errors:\n{report}")
    write_registry(registry, Path(REGISTRY_FILENAME))
    print(f"Wrote {REGISTRY_FILENAME} with {len(registry)} components.")

    print("Loading BLS relative-importance workbook...")
    ri_data = load_current_relative_importance(items_df, force=force)
    print(
        f"Mapped RI values for {len(ri_data.ri_by_code)} item codes "
        f"(vintage={ri_data.weight_vintage}, dec={ri_data.december_month})."
    )
    if ri_data.unmatched_names:
        print(f"RI names not mapped to cu.item: {len(ri_data.unmatched_names)}")

    current_year = date.today().year
    print("Resolving latest CPI reference month...")
    probe_records = fetch_series_data(
        ["CUUR0000SA0", "CUSR0000SA0"],
        current_year - 2,
        current_year,
        force=force,
    )
    probe_nsa = records_to_wide(probe_records[probe_records["series_id"].str.startswith("CUUR")], ["CUUR0000SA0"])
    probe_sa = records_to_wide(probe_records[probe_records["series_id"].str.startswith("CUSR")], ["CUSR0000SA0"])
    latest_probe_months = latest_common_months(probe_nsa, probe_sa, count=3)
    latest_month = latest_probe_months[-1]
    print(f"Latest reference month: {month_display(latest_month)}")

    # Pull an extra year so derived m/m and 10-year dashboard volatility have
    # a prior month available at the start of the displayed lookback.
    start_year = int(latest_month.year) - 11
    end_year = int(latest_month.year)
    nsa_series = [entry["series_nsa"] for entry in registry if entry.get("series_nsa")]
    sa_series = [entry["series_sa"] for entry in registry if entry.get("series_sa")]
    all_series = sorted(set(nsa_series + sa_series))
    print(f"Fetching {len(all_series)} CPI series for {start_year}-{end_year}...")
    records = fetch_series_data(all_series, start_year, end_year, force=force)

    wide_nsa = records_to_wide(
        records[records["series_id"].isin(nsa_series)].copy(),
        nsa_series,
    )
    wide_sa = records_to_wide(
        records[records["series_id"].isin(sa_series)].copy(),
        sa_series,
    )
    latest_months = latest_common_months(wide_nsa, wide_sa, count=3)
    print("Latest 3 months:", ", ".join(month_display(month) for month in latest_months))

    rel_summary = release_summary(force)
    output_path = Path(args.output)
    print(f"Writing workbook to {output_path}...")
    build_info = build_workbook(
        output_path,
        registry,
        ri_data,
        wide_nsa,
        wide_sa,
        latest_months,
        rel_summary,
    )

    if build_info.formula_error_literals:
        report = "\n".join(build_info.formula_error_literals[:50])
        raise SystemExit(f"Formula-error literal scan failed:\n{report}")

    if not build_info.libreoffice_checked:
        print("LibreOffice/soffice was not found; formula cache recalculation was skipped.")

    print(f"Done: {build_info.path}")
    print(f"Data as of {month_display(build_info.latest_month)}")


if __name__ == "__main__":
    main()
