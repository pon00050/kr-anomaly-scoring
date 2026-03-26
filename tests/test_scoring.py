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


# ── score_events functional tests ─────────────────────────────────────────────

def _make_pv_with_volume_surge(ticker, issue_date_str, baseline_vol=100_000, event_vol=2_000_000):
    """Build a price/volume DataFrame that produces a volume_ratio > 3.0.

    Layout: 100 pre-issue rows at baseline_vol, 30 post-issue rows at event_vol.
    With defaults: df_pre (rows 10-39) mean = 100K; df_window (rows 40-129) mean ~733K.
    Resulting volume_ratio ≈ 7.3, well above the VOLUME_SURGE_RATIO = 3.0 threshold.

    PRICE_WINDOW_TRADING_DAYS = 60:
      issue_idx = 100; window_start = 40; df_pre = rows[10:40] (baseline);
      df_window = rows[40:130] (60 baseline + 30 event rows).
    """
    issue_date = pd.Timestamp(issue_date_str)
    pre_dates = pd.date_range(end=issue_date - pd.Timedelta(days=1), periods=100, freq="B")
    post_dates = pd.date_range(start=issue_date + pd.Timedelta(days=1), periods=30, freq="B")
    all_dates = pre_dates.append(post_dates)
    volumes = [baseline_vol] * len(pre_dates) + [event_vol] * len(post_dates)
    closes = [10000.0] * len(all_dates)
    return pd.DataFrame({"ticker": ticker, "date": all_dates, "close": closes, "volume": volumes})


def test_score_events_volume_flag_triggered():
    from kr_anomaly_scoring._scoring import score_events

    corp_code = "00126380"
    ticker = "035720"
    issue_date_str = "2022-06-01"

    df_cb = pd.DataFrame({
        "corp_code": [corp_code],
        "issue_date": ["20220601"],
        "bond_type": ["CB"],
        "exercise_price": [10000.0],
        "issue_amount": [5_000_000_000.0],
        "refixing_floor": [np.nan],
        "repricing_history": ["[]"],
        "exercise_events": ["[]"],
    })
    df_pv = _make_pv_with_volume_surge(ticker, issue_date_str)
    df_oh = pd.DataFrame(columns=["corp_code", "date", "change_shares"])
    df_map = pd.DataFrame({"corp_code": [corp_code], "ticker": [ticker]})

    result = score_events(df_cb, df_pv, df_oh, df_map)

    assert not result.empty
    row = result.iloc[0]
    assert row["volume_flag"] is True or row["volume_flag"] == True
    assert row["anomaly_score"] >= 1


def test_score_events_no_false_flag():
    from kr_anomaly_scoring._scoring import score_events

    corp_code = "00999999"
    ticker = "999999"
    issue_date_str = "2022-06-01"

    df_cb = pd.DataFrame({
        "corp_code": [corp_code],
        "issue_date": ["20220601"],
        "bond_type": ["CB"],
        "exercise_price": [10000.0],
        "issue_amount": [1_000_000_000.0],
        "refixing_floor": [np.nan],
        "repricing_history": ["[]"],
        "exercise_events": ["[]"],
    })
    # Flat volume across all dates — ratio = 1.0, well below 3.0 threshold
    df_pv = _make_pv_with_volume_surge(ticker, issue_date_str, baseline_vol=100_000, event_vol=100_000)
    df_oh = pd.DataFrame(columns=["corp_code", "date", "change_shares"])
    df_map = pd.DataFrame({"corp_code": [corp_code], "ticker": [ticker]})

    result = score_events(df_cb, df_pv, df_oh, df_map)

    assert not result.empty
    row = result.iloc[0]
    assert row["volume_flag"] is False or row["volume_flag"] == False
    assert row["repricing_flag"] is False or row["repricing_flag"] == False
    assert row["exercise_cluster_flag"] is False or row["exercise_cluster_flag"] == False
    assert row["holdings_flag"] is False or row["holdings_flag"] == False
    assert row["anomaly_score"] == 0


# ── score_disclosures functional tests ────────────────────────────────────────

def _make_disc_df(corp_code, trading_date_str, is_material=True):
    """Build a minimal disclosure DataFrame."""
    return pd.DataFrame({
        "corp_code": [corp_code],
        "trading_date": pd.to_datetime([trading_date_str]),
        "disclosure_type": ["CB"],
        "title": ["전환사채권 발행결정"],
        "is_material": [is_material],
        "dart_link": ["https://dart.fss.or.kr/"],
    })


def _make_pv_disc(ticker, date_str, price_change_pct, volume_ratio):
    """Build a price/volume DataFrame for disclosure scoring (needs price_change_pct, volume_ratio)."""
    return pd.DataFrame({
        "ticker": [ticker],
        "date": pd.to_datetime([date_str]),
        "price_change_pct": [price_change_pct],
        "volume_ratio": [volume_ratio],
    })


def test_score_disclosures_flag_triggered():
    from kr_anomaly_scoring._scoring import score_disclosures

    corp_code = "00126380"
    ticker = "035720"
    date_str = "2022-06-01"

    df_disc = _make_disc_df(corp_code, date_str, is_material=True)
    # price_change_pct=6.0 >= 5.0 threshold; volume_ratio=3.0 >= 2.0 threshold
    df_pv = _make_pv_disc(ticker, date_str, price_change_pct=6.0, volume_ratio=3.0)
    df_map = pd.DataFrame({"corp_code": [corp_code], "ticker": [ticker]})

    result = score_disclosures(df_disc, df_pv, df_map)

    assert not result.empty
    flagged = result[result["flag"] == True]
    assert not flagged.empty


def test_score_disclosures_no_false_flag():
    from kr_anomaly_scoring._scoring import score_disclosures

    corp_code = "00999999"
    ticker = "999999"
    date_str = "2022-06-01"

    df_disc = _make_disc_df(corp_code, date_str, is_material=True)
    # price_change_pct=1.0 < 3.0 borderline threshold — row excluded entirely
    df_pv = _make_pv_disc(ticker, date_str, price_change_pct=1.0, volume_ratio=0.5)
    df_map = pd.DataFrame({"corp_code": [corp_code], "ticker": [ticker]})

    result = score_disclosures(df_disc, df_pv, df_map)

    # Either empty or no flagged rows
    if not result.empty:
        assert (result["flag"] == False).all()
