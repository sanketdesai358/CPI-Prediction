from datetime import date

from cpi_model.costar_adr import ADRRelease, parse_release_text, weekly_month


def test_parse_weekly_release_uses_national_labeled_values() -> None:
    text = """
    25 June 2026
    14-20 June 2026 (percentage change from comparable week in 2025):
    Occupancy: 71.3% (+1.2%)
    Average daily rate (ADR): US$178.03 (+8.4%)
    Revenue per available room (RevPAR): US$126.86 (+9.7%)
    San Francisco ADR (+53.5% to US$301.35)
    """
    row = parse_release_text(text, title="U.S. hotel results for week ending 20 June", url="https://example.test/weekly")
    assert row is not None
    assert row.adr == 178.03
    assert row.occupancy == 71.3
    assert row.week_start == "2026-06-14"
    assert row.week_end == "2026-06-20"


def test_weekly_month_day_weights_cross_month_week() -> None:
    row = ADRRelease(
        cadence="weekly",
        title="week",
        url="https://example.test/week",
        publication_date="2026-07-09",
        adr=170.0,
        occupancy=70.0,
        revpar=119.0,
        week_start="2026-06-28",
        week_end="2026-07-04",
    )
    june = weekly_month([row], "2026-06", as_of=date(2026, 7, 9), carry_forward=False)
    july = weekly_month([row], "2026-07", as_of=date(2026, 7, 9), carry_forward=False)
    assert june and june["observedDays"] == 3
    assert july and july["observedDays"] == 4
    assert june["adr"] == july["adr"] == 170.0
