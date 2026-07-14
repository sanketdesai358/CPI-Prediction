# Release scoring artifacts

After each CPI release:

1. Refresh BLS actuals.
2. Run `python -m cpi_model.score --month YYYY-MM`.
3. Rebuild the local-only `cpi-model-archive/Actual_vs_Predicted_June_2026.xlsx` workbook with `build_forecast_history.mjs`.

The workbook rebuilds from every scored `cpi-model/runs/YYYY-MM/score.json` artifact. It is intentionally excluded from the dashboard and Vercel deployment.
