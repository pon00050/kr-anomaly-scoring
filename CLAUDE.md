# kr-anomaly-scoring
> Anomaly scoring for CB/BW issuances: timing anomalies, officer network analysis, and Beneish screening — reads parquets from kr-dart-pipeline.

## Install & Test
```bash
uv sync
uv run pytest tests/ -v
```

## Architecture

Package root: `kr_anomaly_scoring/`

- `_scoring.py` — Core scoring functions (repricing discount, exercise peak, volume surge, holdings decrease).
- `beneish_screen.py` — Applies kr-beneish M-Score to anomaly candidates.
- `timing_anomalies.py` — Detects anomalous trading timing around CB/BW issuance dates.
- `cb_bw_timelines.py` — Marimo notebook: CB/BW timeline visualization (interactive).
- `officer_network.py` — Officer network graph construction from DART disclosures.
- `run_*.py` — CLI entry points: `run_cb_bw_timelines.py`, `run_timing_anomalies.py`, `run_officer_network.py`.

Reads parquets from `kr_forensic_core.paths.data_dir()` — same directory written by kr-dart-pipeline.

## Conventions
- Package manager: `uv`
- Build system: hatchling
- Test command: `uv run pytest tests/ -v`
- All paths via `kr_forensic_core.paths.data_dir()`
- No `sys.path` manipulation — removed in March 2026

## Key Decisions
- `sys.path.insert` was removed from `__init__.py` in March 2026 (same issue as kr-dart-pipeline).
- Marimo cells in `cb_bw_timelines.py` use `kr_anomaly_scoring._scoring` absolute imports (not bare `_scoring`) to work correctly when installed as a package.
- Scoring thresholds are defined in `kr_forensic_core.constants` — not duplicated here.

## Known Gaps

| Gap | Why | Status |
|-----|-----|--------|
| Officer network scoring not wired into main pipeline | Requires SEIBRO officer registration data (blocked) — see XB-002 | Blocked — SEIBRO API ETA end of April 2026 |
| No end-to-end test with real parquets | Requires kr-dart-pipeline outputs in CI | Deferred |


---

**Working notes** (regulatory analysis, legal compliance research, or anything else not appropriate for this public repo) belong in the gitignored working directory of the coordination hub. Engineering docs (API patterns, test strategies, run logs) stay here.
