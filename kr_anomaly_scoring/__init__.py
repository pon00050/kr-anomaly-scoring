"""kr-anomaly-scoring — CB/BW + timing + officer network anomaly scoring.

Scores Korean listed companies for:
1. Convertible bond / bond-with-warrant manipulation (4 flags)
2. Disclosure timing anomalies (price/volume movement around filings)
3. Officer network connections and centrality

Usage:
    from kr_anomaly_scoring import score_cb_bw_events, score_disclosures
    df_results = score_cb_bw_events(df_cb, df_pv, df_oh, df_map)
    df_timing  = score_disclosures(df_disc, df_pv, df_map)
"""

from __future__ import annotations

from kr_anomaly_scoring._scoring import score_events as score_cb_bw_events  # noqa: F401
from kr_anomaly_scoring._scoring import score_disclosures  # noqa: F401

__version__ = "1.0.0"
__all__ = ["score_cb_bw_events", "score_disclosures"]
