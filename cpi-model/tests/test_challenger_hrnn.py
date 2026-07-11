from challenger.hrnn.run import build_comparison


def test_challenger_artifact_has_required_sections() -> None:
    payload = build_comparison()
    assert payload["status"] == "complete_fast_research_run"
    assert set(payload["windows"]) == {"A", "B", "C"}
    assert payload["componentLeague"]
    assert payload["hierarchyLevelMetrics"]
    gasoline_rows = payload["componentSeries"]["SETB01"]
    assert gasoline_rows
    keys = [
        "productionTier1NsaMm",
        "productionTier3NsaMm",
        "hrnnNsaMm",
        "iGruNsaMm",
        "seasonalArNsaMm",
    ]
    for row in gasoline_rows:
        values = [row[key] for key in keys]
        assert values[0] is not None, f"Missing EIA gasoline measurement for {row['month']}"
        assert all(value == values[0] for value in values[1:]), (
            f"Challenger gasoline inputs diverged for {row['month']}: "
            f"{dict(zip(keys, values))}"
        )


def test_challenger_keeps_variants_separate() -> None:
    payload = build_comparison()
    metrics = payload["windows"]["C"]["metrics"]
    assert "hrnnHeadlineNsaMmMae" in metrics
    assert "iGruHeadlineNsaMmMae" in metrics
    assert "seasonalArHeadlineNsaMmMae" in metrics
