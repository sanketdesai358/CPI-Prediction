from __future__ import annotations

from pathlib import Path

from cpi_excel.constants import REGISTRY_FILENAME
from cpi_excel.labstat import load_items, load_series, read_registry, validate_registry


def test_registry_validates_against_labstat() -> None:
    registry_path = Path(REGISTRY_FILENAME)
    assert registry_path.exists(), "Run python build_workbook.py before pytest."
    registry = read_registry(registry_path)
    errors = validate_registry(registry, load_items(), load_series())
    assert errors == []
