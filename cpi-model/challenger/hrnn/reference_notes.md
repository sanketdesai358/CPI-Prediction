# HRNN Challenger Reference Notes

Reference paper:

- Barkan, Oren; Benchimol, Jonathan; Caspi, Itamar; Cohen, Eliya; Hammer, Allon; Koenigstein, Noam. "Forecasting CPI inflation components with hierarchical recurrent neural networks." International Journal of Forecasting, 39(3), 1145-1162, 2023.

Reference implementation reviewed:

- https://github.com/AllonHammer/CPI_HRNN
- The repository exposes a PyTorch implementation with `hierarchical_gru.py`, `model/h_gru_model.py`, `model/gru_model.py`, and `utils/utils.py`.
- Its dataset schema is a parsed BLS CPI hierarchy with `Date`, `Category`, `Category_id`, `Price`, `Weight`, `Indent`, `Parent`, and `Parent ID`.
- Its preprocessing target is monthly inflation computed as `100 * log(x_t / x_{t-1})`.
- Its HRNN trains one GRU per category. For non-root nodes, the loss includes a Gaussian prior that pulls child GRU parameters toward parent GRU parameters.
- Prior strength is computed from the parent-child correlation; the exponential variant uses `n = exp(alpha + corr)`.
- The paper also reports non-hierarchical GRU and classical controls, plus hierarchy-level summaries.

Local adaptation choices:

- This repo builds the node graph from the current BLS `cu.item`/dashboard cache hierarchy rather than the paper's fixed 1994-2019 snapshot.
- The first committed runner is intentionally additive and does not modify production forecasts.
- The default runner is a deterministic, fast HRNN-style challenger that preserves the data contract and evaluation rules while avoiding a multi-hour 400+ PyTorch GRU training job during dashboard builds. It uses the paper's endogenous-only inputs, parent-child correlation, and hierarchy shrinkage equation to produce reproducible artifacts.
- Gasoline is the single external exception. It uses the cached EIA gasoline monthly-average measurement model when available.
- A full PyTorch MAP trainer can be plugged into the same artifact schema later; dashboard routes only consume precomputed JSON and never train on page load.

Known limitations in the initial artifact:

- The checked-in comparison is a fast deterministic challenger run, not a full neural GRU checkpoint sweep.
- Historical relative importance uses the per-month `ri` embedded in the dashboard cache where present, falling back to current RI only when an archived value is missing.
- Current BLS hierarchy is used for all historical months. Components whose parents changed historically are flagged as a choice in the report rather than silently reconstructed.
