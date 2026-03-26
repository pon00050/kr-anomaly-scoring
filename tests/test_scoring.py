"""Tests for kr-anomaly-scoring package."""

import pandas as pd
import numpy as np
from pathlib import Path


def test_package_importable():
    import kr_anomaly_scoring
    assert kr_anomaly_scoring.__version__ == "1.0.0"


def test_score_cb_bw_events_importable():
    from kr_anomaly_scoring import score_cb_bw_events
    assert callable(score_cb_bw_events)


def test_score_disclosures_importable():
    from kr_anomaly_scoring import score_disclosures
    assert callable(score_disclosures)


def test_scoring_module_importable():
    from kr_anomaly_scoring._scoring import score_events, score_disclosures
    assert callable(score_events)
    assert callable(score_disclosures)


def test_no_krff_imports():
    """None of the scoring scripts should import from krff (delivery shell)."""
    pkg_dir = Path(__file__).resolve().parents[1] / "kr_anomaly_scoring"
    violations = []
    for py_file in pkg_dir.glob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="replace")
        if "from krff" in text or "import krff" in text:
            violations.append(py_file.name)
    assert not violations, f"Scripts import from krff (delivery shell): {violations}"


def test_score_events_empty_inputs():
    """score_events returns empty DataFrame on empty inputs without error."""
    from kr_anomaly_scoring import score_cb_bw_events
    # Need minimal column structure for the function to not blow up on groupby
    df_cb = pd.DataFrame(columns=["corp_code", "issue_date", "bond_type"])
    df_pv = pd.DataFrame(columns=["ticker", "date", "close", "volume"])
    df_oh = pd.DataFrame(columns=["corp_code", "date", "change_shares"])
    df_map = pd.DataFrame(columns=["corp_code", "ticker"])
    result = score_cb_bw_events(df_cb, df_pv, df_oh, df_map)
    assert isinstance(result, pd.DataFrame)


def test_score_events_returns_expected_columns():
    """score_events returns the expected output columns."""
    from kr_anomaly_scoring import score_cb_bw_events

    # Minimal synthetic inputs — 3 rows of price data to create a real window
    tickers = ["035720"] * 3
    dates = pd.to_datetime(["2021-10-01", "2022-01-05", "2022-03-01"])
    df_cb = pd.DataFrame({
        "corp_code": ["00126380"],
        "issue_date": ["20220101"],
        "bond_type": ["CB"],
        "exercise_price": [10000.0],
        "issue_amount": [5000000000.0],
        "refixing_floor": [np.nan],
        "repricing_history": ["[]"],
        "exercise_events": ["[]"],
    })
    df_pv = pd.DataFrame({
        "ticker": tickers,
        "date": dates,
        "close": [100000.0, 95000.0, 98000.0],
        "volume": [1000000, 1500000, 900000],
        "price_change_pct": [1.5, -3.0, 2.0],
        "volume_ratio": [1.2, 2.5, 0.8],
    })
    df_oh = pd.DataFrame(columns=["corp_code", "date", "change_shares"])
    df_map = pd.DataFrame({"corp_code": ["00126380"], "ticker": ["035720"]})

    result = score_cb_bw_events(df_cb, df_pv, df_oh, df_map)
    assert isinstance(result, pd.DataFrame)
    if not result.empty:
        assert "anomaly_score" in result.columns
        assert "flag_count" in result.columns
        assert "repricing_flag" in result.columns


def test_score_disclosures_empty_inputs():
    """score_disclosures returns empty DataFrame on empty inputs."""
    from kr_anomaly_scoring import score_disclosures
    result = score_disclosures(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert isinstance(result, pd.DataFrame)


def test_constants_come_from_core():
    """Verify constants used in _scoring come from kr_forensic_core, not krff."""
    from kr_forensic_core.constants import (
        FLAG_REPRICING_BELOW_MARKET,
        FLAG_EXERCISE_AT_PEAK,
        FLAG_VOLUME_SURGE,
        FLAG_HOLDINGS_DECREASE,
        REPRICING_DISCOUNT_RATIO,
        VOLUME_SURGE_RATIO,
    )
    assert FLAG_REPRICING_BELOW_MARKET == "repricing_below_market"
    assert FLAG_EXERCISE_AT_PEAK == "exercise_at_peak"
    assert VOLUME_SURGE_RATIO == 3.0
    assert REPRICING_DISCOUNT_RATIO == 0.95
