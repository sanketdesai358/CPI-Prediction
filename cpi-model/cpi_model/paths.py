from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
DASHBOARD_ROOT = WORKSPACE / "cpi-dashboard"
EXCEL_ROOT = WORKSPACE / "cpi-excel"

REGISTRY_PATH = ROOT / "registry.json"
EXTENDED_REGISTRY_PATH = ROOT / "extended_registry.json"
DASHBOARD_CACHE_PATH = DASHBOARD_ROOT / "src" / "data" / "dashboard-cache.json"
RUNS_DIR = ROOT / "runs"
BACKTEST_DIR = ROOT / "backtest"
TRIAGE_REPORT_PATH = ROOT / "triage_report.md"
MODEL_CARD_PATH = ROOT / "MODEL_CARD.md"
