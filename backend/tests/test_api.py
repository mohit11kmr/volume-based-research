import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from main import app
from services.stock_data import generate_synthetic_stock_data
from services.volume_analytics import compute_volume_metrics, calculate_volume_profile
from services.backtester import run_volume_backtest
from services.learning_brain import predict_ml_win_probability

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "online"


def test_stocks_endpoint_returns_list():
    res = client.get("/api/stocks")
    assert res.status_code == 200
    payload = res.json()
    stocks = payload.get("stocks", payload if isinstance(payload, list) else [])
    assert isinstance(stocks, list) and len(stocks) > 0
    assert all("symbol" in s for s in stocks)
    assert payload.get("universe") == "NIFTY 50 + US Tech"


def test_analysis_endpoint_schema():
    res = client.get("/api/stocks/RELIANCE.NS")
    assert res.status_code == 200
    data = res.json()
    assert "candles" in data
    assert "volumeProfile" in data
    assert "aiReport" in data
    assert "mlPrediction" in data
    assert data["dataSource"] in ("yfinance", "synthetic")
    assert data["isSynthetic"] == (data["dataSource"] == "synthetic")


def test_screener_endpoint_schema():
    res = client.get("/api/screener?min_surge=1.5")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "count" in data


def test_backtest_endpoint_schema():
    res = client.post("/api/backtest", json={
        "symbol": "RELIANCE.NS",
        "volumeMultiplier": 2.0,
        "holdingDays": 5,
        "stopLossPct": 2.0,
        "takeProfitPct": 6.0,
        "initialCapital": 100000.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "totalReturnPct" in data
    assert "winRatePct" in data
    assert "maxDrawdownPct" in data
    assert "totalTrades" in data
    assert "winningTrades" in data
    assert "losingTrades" in data


def test_synthetic_data_is_marked():
    df = generate_synthetic_stock_data("TEST.NS", days=50)
    assert df.attrs.get("dataSource") == "synthetic"


def test_volume_metrics_no_lookahead_columns():
    df = generate_synthetic_stock_data("TEST.NS", days=60)
    out = compute_volume_metrics(df)
    assert "Vol_Surge_Ratio" in out.columns
    assert "OBV" in out.columns
    assert "CMF" in out.columns


def test_volume_profile_poc_flag():
    df = generate_synthetic_stock_data("TEST.NS", days=60)
    out = compute_volume_metrics(df)
    profile = calculate_volume_profile(out, bins_count=12)
    assert profile
    assert sum(1 for p in profile if p["isPOC"]) == 1


def test_ml_prediction_bounds():
    res = predict_ml_win_probability(2.0, 0.2, "RISING")
    assert 1.0 <= res["mlWinProbabilityPct"] <= 98.0
    assert "confidenceLabel" in res


def test_backtest_returns_consistent_counts():
    df = generate_synthetic_stock_data("TEST.NS", days=300)
    res = run_volume_backtest(df, volume_multiplier=2.0, holding_days=5)
    assert res["totalTrades"] == res["winningTrades"] + res["losingTrades"]


def test_enhanced_volume_indicators_present():
    df = generate_synthetic_stock_data("TEST.NS", days=60)
    out = compute_volume_metrics(df)
    for col in ["ADL", "ADL_EMA20", "MFI", "VPT", "Volume_ZScore", "Pocket_Pivot"]:
        assert col in out.columns
    assert out["MFI"].between(0, 100).all()


def test_scenarios_walk_forward_fields():
    df = generate_synthetic_stock_data("TEST.NS", days=300)
    from services.scenario_generator import evaluate_and_rank_scenarios
    res = evaluate_and_rank_scenarios(df, "TEST.NS")
    assert "error" not in res
    assert res["isOutOfSampleValidated"] is True
    assert res["validationMethod"].startswith("walk-forward")
    assert res["trainWindow"]["bars"] + res["testWindow"]["bars"] == len(df)
    for scn in res["topScenarios"]:
        assert "outOfSample" in scn
        assert "isZeroLossValidated" in scn


def test_value_area_computed():
    df = generate_synthetic_stock_data("TEST.NS", days=60)
    out = compute_volume_metrics(df)
    profile = calculate_volume_profile(out, bins_count=12)
    from services.volume_analytics import calculate_value_area
    va = calculate_value_area(profile)
    assert va["vah"] > 0 and va["val"] > 0
    assert va["poc"] > 0


def test_paper_trading_per_user_isolation():
    from services.risk_engine import PaperTradingManager
    mgr = PaperTradingManager(initial_capital=100000.0)
    sim_a = mgr.get("user-A")
    sim_b = mgr.get("user-B")
    sim_a.execute_paper_buy("RELIANCE.NS", current_price=100.0)
    assert len(sim_a.open_positions) == 1
    assert len(sim_b.open_positions) == 0
    assert len(mgr.get("user-A").open_positions) == 1


def test_nse_direct_fetch_graceful():
    from services.stock_data import _fetch_nse_direct_quote
    quote = _fetch_nse_direct_quote("NOTAVALIDSYMBOLXX.NS")
    assert quote is None or quote.get("symbol")
