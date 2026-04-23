# kr-anomaly-scoring

**[Read the full write-up →](https://ronanwrites.vercel.app/manuals/forensic-platform-architecture)**

CB/BW + timing + officer network anomaly scoring for Korean listed companies.

Part of the [forensic accounting toolkit](https://github.com/pon00050/forensic-accounting-toolkit) ecosystem.

## Usage

```python
from kr_anomaly_scoring import score_cb_bw_events, score_disclosures

# Score convertible bond / bond-with-warrant events (4 flags)
df_results = score_cb_bw_events(df_cb, df_pv, df_oh, df_map)

# Score disclosure timing anomalies
df_timing = score_disclosures(df_disc, df_pv, df_map)
```

## Install

```bash
uv add git+https://github.com/pon00050/kr-anomaly-scoring
# With Marimo interactive dashboards:
uv add "git+https://github.com/pon00050/kr-anomaly-scoring[marimo]"
```

## Scoring Flags (CB/BW)

| Flag | Description | Threshold |
|------|-------------|-----------|
| `repricing_below_market` | Repricing adjusted below 95% of market price | `REPRICING_DISCOUNT_RATIO = 0.95` |
| `exercise_at_peak` | Exercise within 5 calendar days of price peak | `EXERCISE_PEAK_WINDOW_CALENDAR_DAYS = 5` |
| `volume_surge` | Volume ratio > 3x pre-event baseline | `VOLUME_SURGE_RATIO = 3.0` |
| `holdings_decrease` | Officer holdings decrease post-exercise | `HOLDINGS_DECREASE_RATIO = 0.95` |

## Data Requirements

Set `KRFF_DATA_DIR` or pass `--data-dir` to point to the processed parquet directory:

```
01_Data/processed/
  cb_bw_events.parquet
  price_volume.parquet
  officer_holdings.parquet
  corp_ticker_map.parquet
  disclosures.parquet
```
