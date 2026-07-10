from challenger.hrnn.run import build_comparison


def test_challenger_artifact_has_required_sections() -> None:
    payload = build_comparison()
    assert payload["status"] == "complete_fast_research_run"
    assert set(payload["windows"]) == {"A", "B", "C"}
    assert payload["componentLeague"]
    assert payload["hierarchyLevelMetrics"]


def test_challenger_keeps_variants_separate() -> None:
    payload = build_comparison()
    metrics = payload["windows"]["C"]["metrics"]
    assert "hrnnHeadlineNsaMmMae" in metrics
    assert "iGruHeadlineNsaMmMae" in metrics
    assert "seasonalArHeadlineNsaMmMae" in metrics
