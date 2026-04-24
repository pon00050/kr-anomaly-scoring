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

---

## NEVER commit to this repo

This repository is **public**. Before staging or writing any new file, check the list below. If the content matches any item, route it to the gitignored working directory of the coordination hub instead, NOT to this repo.

**Hard NO list:**

1. **Any API key, token, or credential — even a truncated fingerprint.** This includes Anthropic key fingerprints (sk-ant-...), AWS keys (AKIA...), GitHub tokens (ghp_...), DART/SEIBRO/KFTC API keys, FRED keys. Even partial / display-truncated keys (e.g. "sk-ant-api03-...XXXX") leak the org-to-key linkage and must not be committed.
2. **Payment / billing data of any kind.** Card numbers (full or last-four), invoice IDs, receipt numbers, order numbers, billing-portal URLs, Stripe/Anthropic/PayPal account states, monthly-spend caps, credit balances.
3. **Vendor support correspondence.** Subject lines, body text, ticket IDs, or summaries of correspondence with Anthropic / GitHub / Vercel / DART / any vendor's support team.
4. **Named third-party outreach targets.** Specific company names, hedge-fund names, audit-firm names, regulator-individual names appearing in a planning, pitch, or outreach context. Engineering content discussing Korean financial institutions in a neutral domain context (e.g. "DART is the FSS disclosure system") is fine; planning text naming them as a sales target is not.
5. **Commercial-positioning memos.** Documents discussing buyer segments, monetization models, pricing strategy, competitor analysis, market positioning, or go-to-market plans. Research methodology and technical roadmaps are fine; commercial strategy is not.
6. **Files matching the leak-prevention .gitignore patterns** (*_prep.md, *_billing*, *_outreach*, *_strategy*, *_positioning*, *_pricing*, *_buyer*, *_pitch*, product_direction.md, etc.). If you find yourself wanting to write a file with one of these names, that is a signal that the content belongs in the hub working directory.

**When in doubt:** put the content in the hub working directory (gitignored), not this repo. It is always safe to add later. It is expensive to remove after force-pushing — orphaned commits remain resolvable on GitHub for weeks.

GitHub Push Protection is enabled on this repo and will reject pushes containing well-known credential patterns. That is a backstop, not the primary defense — write-time discipline is.
