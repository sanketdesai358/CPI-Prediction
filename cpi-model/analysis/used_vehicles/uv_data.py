"""Data loaders for the Manheim-vs-BLS used-vehicle pass-through study.

Two sources, both real (no fabricated / hand-typed values anywhere):

1. Manheim Used Vehicle Value Index (MUVVI) -- the seasonally-adjusted,
   mix/mileage-adjusted wholesale auction index.  Pulled live from Cox
   Automotive's public monthly "web-table-data" XLSX (the same spreadsheet the
   monthly UVVI press releases link to).  If the live pull fails, we fall back
   to a maintained manual CSV; if neither is present we STOP LOUDLY and print
   exactly what to paste.  We never invent index values.

2. BLS "used cars and trucks" CPI:
     CUSR0000SETA02  -- seasonally adjusted   (PRIMARY, matches Manheim's SA)
     CUUR0000SETA02  -- not seasonally adj.   (reference only)
   Pulled via the BLS public API v2 with the key already in the repo-root .env.

Run this module directly to (re)build the cached raw + merged CSVs and print a
provenance summary.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent            # ...\cpi-model\analysis\used_vehicles
CPI_MODEL = HERE.parents[1]                        # ...\cpi-model
REPO_ROOT = HERE.parents[2]                        # ...\c-users-...-cpi (holds .env)
ENV_PATH = REPO_ROOT / ".env"
MANUAL_CSV = CPI_MODEL / "data" / "manual" / "manheim_uvvi.csv"
RAW_MANHEIM = HERE / "manheim_uvvi_raw.csv"
RAW_BLS = HERE / "bls_seta02_raw.csv"

# Current public Manheim UVVI "web-table-data" workbook.  Cox re-publishes this
# monthly under /wp-content/uploads/YYYY/MM/<Mon>-<YYYY>-Manheim-Used-Vehicle-
# Value-Index.xlsx and links it from each monthly UVVI press release.  Verified
# reachable (HTTP 200, real XLSX) on 2026-07-07; full monthly history from
# 1997-01 (base Jan-1997 = 100).  Update this when a newer month publishes.
MANHEIM_XLSX_URL = (
    "https://www.coxautoinc.com/wp-content/uploads/2026/06/"
    "May-2026-Manheim-Used-Vehicle-Value-Index.xlsx"
)
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

BLS_SERIES = {
    "CUSR0000SETA02": "cpi_used_sa",   # seasonally adjusted (primary)
    "CUUR0000SETA02": "cpi_used_nsa",  # not seasonally adjusted (reference)
}


class DataUnavailable(RuntimeError):
    """Raised (loudly) when a required real data source cannot be reached."""


# --------------------------------------------------------------------------- #
# Manheim
# --------------------------------------------------------------------------- #
def _parse_manheim_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise a raw Manheim web-table frame into date/index_sa columns.

    The published DATA sheet columns are:
      date | Index (1/97 = 100) | Manheim Index $ amount SA | Seasonal adjustment
      factor | Manheim Index $ amount NSA | SA Price % MoM | Index % MoM |
      Index % YoY | NSA Price % MoM | NSA Price % YoY
    The manual-CSV fallback uses the simpler schema documented in the STOP
    message: date,index (index = the SA "Index (1/97 = 100)" level).
    """
    df = df.copy()
    df = df.rename(columns={df.columns[0]: "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()

    idx_col = None
    for cand in ("Index (1/97 = 100)", "index_sa", "index"):
        if cand in df.columns:
            idx_col = cand
            break
    if idx_col is None:
        # last resort: first numeric column that looks like an index (50-500)
        for c in df.columns:
            if c == "date":
                continue
            s = pd.to_numeric(df[c], errors="coerce")
            if s.between(50, 500).mean() > 0.8:
                idx_col = c
                break
    if idx_col is None:
        raise DataUnavailable("Could not locate the Manheim SA index column.")

    out = pd.DataFrame(
        {"date": df["date"], "manheim_sa": pd.to_numeric(df[idx_col], errors="coerce")}
    ).dropna(subset=["manheim_sa"])
    # keep NSA if present for reference
    for cand in ("Manheim Index $ amount NSA", "index_nsa"):
        if cand in df.columns:
            out["manheim_nsa_dollar"] = pd.to_numeric(df[cand], errors="coerce").values
            break
    out = out.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if not out["manheim_sa"].between(50, 500).all():
        raise DataUnavailable("Manheim SA index has values outside the 50-500 sanity band.")
    return out


def _stop_loud(reason: str) -> None:
    msg = f"""
==========================================================================
 MANHEIM UVVI DATA UNAVAILABLE -- STOPPING (no values will be fabricated)
==========================================================================
Reason: {reason}

The loader tried, in order:
  1) manual override CSV : {MANUAL_CSV}
  2) live public XLSX     : {MANHEIM_XLSX_URL}

To proceed, create the manual override CSV and re-run:

  {MANUAL_CSV}

with EXACTLY this schema (one row per month, month-start dates):

  date,index
  1997-01-01,100.0
  1997-02-01,100.33
  ...
  2026-05-01,212.62

Where `index` is the Manheim UVVI *seasonally adjusted* level, the
"Index (1/97 = 100)" column from Cox Automotive's monthly UVVI web-table
spreadsheet. Get it from the current month's release at
https://www.coxautoinc.com/insights/ (search "Manheim Used Vehicle Value
Index <Month> Trends") -> the linked .xlsx -> the DATA sheet.

Do NOT hand-type values from a chart or from memory. Paste the published
column verbatim.
==========================================================================
"""
    print(msg, file=sys.stderr)
    raise DataUnavailable(reason)


def load_manheim(*, cache: bool = True) -> tuple[pd.DataFrame, str]:
    """Return (frame[date, manheim_sa, ...], provenance_string).

    Preference order: manual override CSV -> live Cox XLSX.  Loud stop if both
    fail.  Never fabricates.
    """
    # 1) manual override
    if MANUAL_CSV.exists():
        try:
            df = _parse_manheim_frame(pd.read_csv(MANUAL_CSV))
            prov = f"manual override CSV ({MANUAL_CSV})"
            if cache:
                df.to_csv(RAW_MANHEIM, index=False)
            return df, prov
        except Exception as exc:  # fall through to live if the manual file is broken
            print(f"[warn] manual Manheim CSV present but unreadable: {exc}", file=sys.stderr)

    # 2) live public XLSX
    try:
        r = requests.get(MANHEIM_XLSX_URL, headers=UA, timeout=60)
    except Exception as exc:
        _stop_loud(f"live XLSX request raised {type(exc).__name__}: {exc}")
    if r.status_code != 200 or len(r.content) < 4000:
        _stop_loud(
            f"live XLSX returned HTTP {r.status_code}, {len(r.content)} bytes "
            "(likely moved/blocked)."
        )
    ctype = r.headers.get("content-type", "")
    if "spreadsheet" not in ctype and "excel" not in ctype and "octet-stream" not in ctype:
        _stop_loud(f"live XLSX returned unexpected content-type {ctype!r} (challenge page?).")
    try:
        raw = pd.read_excel(io.BytesIO(r.content), sheet_name="DATA", header=0)
    except Exception as exc:
        _stop_loud(f"downloaded workbook could not be parsed: {type(exc).__name__}: {exc}")
    df = _parse_manheim_frame(raw)
    prov = f"live Cox XLSX ({MANHEIM_XLSX_URL})"
    if cache:
        df.to_csv(RAW_MANHEIM, index=False)
    return df, prov


# --------------------------------------------------------------------------- #
# BLS
# --------------------------------------------------------------------------- #
def _bls_key() -> str:
    if not ENV_PATH.exists():
        raise DataUnavailable(f"No .env at {ENV_PATH}; cannot read BLS_API_KEY.")
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("BLS_API_KEY"):
            return line.split("=", 1)[1].strip()
    raise DataUnavailable("BLS_API_KEY not found in .env.")


def load_bls(*, start_year: int = 1953, cache: bool = True) -> pd.DataFrame:
    """Full-history CPI used cars & trucks (SA + NSA) as a monthly wide frame.

    BLS API v2 caps each request at 20 years, so we pull in chunks.  Guards
    against '-' / '(NA)' placeholder values.
    """
    key = _bls_key()
    end_year = date.today().year
    rows: list[tuple[pd.Timestamp, str, float]] = []
    yr = start_year
    while yr <= end_year:
        chunk_end = min(yr + 19, end_year)
        payload = {
            "seriesid": list(BLS_SERIES),
            "startyear": str(yr),
            "endyear": str(chunk_end),
            "registrationkey": key,
        }
        resp = requests.post(
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
            data=json.dumps(payload),
            headers={"Content-type": "application/json"},
            timeout=90,
        )
        j = resp.json()
        if j.get("status") != "REQUEST_SUCCEEDED":
            raise DataUnavailable(f"BLS API error {yr}-{chunk_end}: {j.get('message')}")
        for s in j["Results"]["series"]:
            name = BLS_SERIES[s["seriesID"]]
            for d in s["data"]:
                if not d["period"].startswith("M"):
                    continue
                v = d["value"].replace(",", "").strip()
                if v in ("", "-", "(NA)"):
                    continue
                ts = pd.Timestamp(int(d["year"]), int(d["period"][1:]), 1)
                rows.append((ts, name, float(v)))
        yr = chunk_end + 1
    if not rows:
        raise DataUnavailable("BLS returned no usable observations.")
    df = (
        pd.DataFrame(rows, columns=["date", "series", "val"])
        .drop_duplicates(["date", "series"])
        .pivot(index="date", columns="series", values="val")
        .sort_index()
        .reset_index()
    )
    if cache:
        df.to_csv(RAW_BLS, index=False)
    return df


# --------------------------------------------------------------------------- #
# Merge
# --------------------------------------------------------------------------- #
def build_merged(*, cache: bool = True) -> tuple[pd.DataFrame, dict]:
    """Merge Manheim SA + BLS SA/NSA on month; add m/m and YoY transforms."""
    manheim, prov = load_manheim(cache=cache)
    bls = load_bls(cache=cache)

    df = pd.merge(manheim[["date", "manheim_sa"]], bls, on="date", how="outer").sort_values("date")
    df = df.set_index("date")

    # m/m % (of monthly index levels) and YoY %
    df["manheim_mom"] = df["manheim_sa"].pct_change() * 100
    df["cpi_sa_mom"] = df["cpi_used_sa"].pct_change() * 100
    df["cpi_nsa_mom"] = df["cpi_used_nsa"].pct_change() * 100
    df["manheim_yoy"] = (df["manheim_sa"] / df["manheim_sa"].shift(12) - 1) * 100
    df["cpi_sa_yoy"] = (df["cpi_used_sa"] / df["cpi_used_sa"].shift(12) - 1) * 100
    df = df.reset_index()

    meta = {
        "manheim_provenance": prov,
        "manheim_span": [
            manheim["date"].min().strftime("%Y-%m"),
            manheim["date"].max().strftime("%Y-%m"),
        ],
        "manheim_n": int(len(manheim)),
        "bls_sa_span": _span(bls, "cpi_used_sa"),
        "bls_nsa_span": _span(bls, "cpi_used_nsa"),
        "bls_series": {k: v for k, v in BLS_SERIES.items()},
        "overlap_span": _span(df.dropna(subset=["manheim_sa", "cpi_used_sa"]), "date_present"),
        "pulled": date.today().isoformat(),
    }
    if cache:
        df.to_csv(HERE / "usedcar_manheim.csv", index=False)
    return df, meta


def _span(frame: pd.DataFrame, col: str) -> list[str] | None:
    if col == "date_present":
        d = frame["date"]
    else:
        d = frame.loc[frame[col].notna(), "date"]
    if d.empty:
        return None
    return [d.min().strftime("%Y-%m"), d.max().strftime("%Y-%m")]


if __name__ == "__main__":
    frame, meta = build_merged()
    print(json.dumps(meta, indent=2))
    print(f"\nMerged rows: {len(frame)}  cols: {list(frame.columns)}")
    print(f"Wrote:\n  {RAW_MANHEIM}\n  {RAW_BLS}\n  {HERE / 'usedcar_manheim.csv'}")
