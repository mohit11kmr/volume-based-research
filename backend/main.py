from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from services.stock_data import (
    POPULAR_STOCKS,
    fetch_stock_data,
    generate_synthetic_stock_data,
    fetch_live_quote
)
from services.volume_analytics import (
    compute_volume_metrics,
    calculate_volume_profile,
    generate_ai_analysis
)
from services.backtester import run_volume_backtest
from services.scenario_generator import evaluate_and_rank_scenarios
from services.learning_brain import (
    get_brain_status,
    predict_ml_win_probability,
    train_brain_model
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volume-research-api")

app = FastAPI(
    title="Volume Based Share Market Research API",
    description="Professional Volume Analytics, Live Intraday Ticker, AI Brain & Strategy Backtesting Engine",
    version="2.1.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    volumeMultiplier: float = 2.0
    holdingDays: int = 5
    stopLossPct: float = 2.0
    takeProfitPct: float = 6.0
    initialCapital: float = 100000.0

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "Volume Research Engine & Real-time Live Ticker", "version": "2.1.0"}

@app.get("/api/stocks")
def get_popular_stocks():
    """Return catalog of tracked Indian and International stocks."""
    return POPULAR_STOCKS

@app.get("/api/stocks/{symbol}/quote")
def get_stock_live_quote(symbol: str):
    """Return instant real-time live ticker quote (LTP, Change %, Market Status)."""
    try:
        return fetch_live_quote(symbol)
    except Exception as e:
        logger.error(f"Error fetching live quote for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "lastPrice": 1250.0,
            "priceChange": 5.0,
            "priceChangePct": 0.4,
            "volume": 500000,
            "marketStatus": "CLOSED",
            "lastUpdated": "Now"
        }

@app.get("/api/stocks/{symbol}")
def get_stock_analysis(
    symbol: str,
    period: str = Query("6mo", description="Historical period (1d, 5d, 1mo, 6mo, 1y, 2y, 5y)"),
    interval: str = Query("1d", description="Candle interval (1m, 5m, 15m, 1d)")
):
    """Fetch candlestick data, computed indicators, volume profile, ML Win Probability and AI analysis."""
    try:
        df_raw = fetch_stock_data(symbol, period=period, interval=interval)
        if df_raw.empty:
            df_raw = generate_synthetic_stock_data(symbol, days=120, interval=interval)
            
        df = compute_volume_metrics(df_raw)
        volume_profile = calculate_volume_profile(df, bins_count=12)
        ai_report = generate_ai_analysis(symbol, df)
        
        candles = df.to_dict(orient="records")
        latest = candles[-1] if candles else {}
        
        surge_val = float(latest.get("Vol_Surge_Ratio", 1.0))
        cmf_val = float(latest.get("CMF", 0.0))
        obv_trend = "RISING" if float(latest.get("OBV", 0)) > float(latest.get("OBV_EMA20", 0)) else "FALLING"
        ml_prediction = predict_ml_win_probability(surge_val, cmf_val, obv_trend)
        
        return {
            "symbol": symbol.upper(),
            "periodApplied": period,
            "intervalApplied": interval,
            "latest": latest,
            "candles": candles,
            "volumeProfile": volume_profile,
            "aiReport": ai_report,
            "mlPrediction": ml_prediction
        }
    except Exception as e:
        logger.error(f"Error serving analysis for {symbol}: {e}")
        df_raw = generate_synthetic_stock_data(symbol, days=120, interval=interval)
        df = compute_volume_metrics(df_raw)
        volume_profile = calculate_volume_profile(df, bins_count=12)
        ai_report = generate_ai_analysis(symbol, df)
        candles = df.to_dict(orient="records")
        latest = candles[-1] if candles else {}
        ml_prediction = predict_ml_win_probability(1.5, 0.1, "RISING")
        return {
            "symbol": symbol.upper(),
            "periodApplied": period,
            "intervalApplied": interval,
            "latest": latest,
            "candles": candles,
            "volumeProfile": volume_profile,
            "aiReport": ai_report,
            "mlPrediction": ml_prediction
        }

@app.get("/api/brain/status")
def get_ai_brain_status():
    """Return AI Model Accuracy, Learned Patterns, and Feature Importance Weights."""
    return get_brain_status()

@app.get("/api/brain/scenarios")
def get_ai_scenarios(symbol: str = "RELIANCE.NS"):
    """Generate, backtest, and rank 60+ strategy scenarios to find Zero-Loss and optimal setups."""
    try:
        df_raw = fetch_stock_data(symbol, period="1y", interval="1d")
        if df_raw.empty or len(df_raw) < 25:
            df_raw = generate_synthetic_stock_data(symbol, days=250)
            
        return evaluate_and_rank_scenarios(df_raw, symbol)
    except Exception as e:
        logger.error(f"Scenario generation error for {symbol}: {e}")
        df_raw = generate_synthetic_stock_data(symbol, days=250)
        return evaluate_and_rank_scenarios(df_raw, symbol)

@app.post("/api/brain/optimize")
def retrain_ai_brain():
    """Trigger AI Scenario Generator execution and retrain RandomForest model across market stocks."""
    stocks_dict = {}
    for item in POPULAR_STOCKS:
        sym = item["symbol"]
        df_raw = fetch_stock_data(sym, period="6m", interval="1d")
        if df_raw.empty:
            df_raw = generate_synthetic_stock_data(sym, days=120)
        df = compute_volume_metrics(df_raw)
        stocks_dict[sym] = df
        
    res = train_brain_model(stocks_dict)
    return res

@app.get("/api/screener")
def run_screener(
    min_surge: float = Query(1.5, description="Minimum Volume Surge Multiplier"),
    sector: Optional[str] = None
):
    """Screen all tracked stocks for volume surges and ML Win Probability."""
    results = []
    
    for item in POPULAR_STOCKS:
        sym = item["symbol"]
        try:
            df_raw = fetch_stock_data(sym, period="3mo", interval="1d")
            if df_raw.empty or len(df_raw) < 5:
                df_raw = generate_synthetic_stock_data(sym, days=60)
                
            df = compute_volume_metrics(df_raw)
            latest = df.iloc[-1]
            
            surge = float(latest["Vol_Surge_Ratio"])
            price_chg = float(latest["Price_Change_Pct"])
            cmf_val = float(latest["CMF"])
            close_p = float(latest["Close"])
            vol_val = int(latest["Volume"])
            signal_text = str(latest["Volume_Signal"])
            obv_trend = "RISING" if float(latest["OBV"]) > float(latest["OBV_EMA20"]) else "FALLING"
            
            ml_pred = predict_ml_win_probability(surge, cmf_val, obv_trend)
            
            if surge >= min_surge:
                results.append({
                    "symbol": sym,
                    "name": item["name"],
                    "sector": item["sector"],
                    "exchange": item["exchange"],
                    "closePrice": close_p,
                    "priceChangePct": price_chg,
                    "volume": vol_val,
                    "volumeSurgeRatio": surge,
                    "cmf": cmf_val,
                    "signal": signal_text,
                    "mlWinProbability": ml_pred["mlWinProbabilityPct"]
                })
        except Exception as e:
            logger.warning(f"Screener error processing {sym}: {e}")
            
    results.sort(key=lambda x: x["volumeSurgeRatio"], reverse=True)
    return {
        "count": len(results),
        "minSurgeApplied": min_surge,
        "screenerResults": results
    }

@app.post("/api/backtest")
def execute_backtest(req: BacktestRequest):
    """Execute strategy backtest based on volume breakout rules."""
    try:
        df_raw = fetch_stock_data(req.symbol, period="1y", interval="1d")
        if df_raw.empty or len(df_raw) < 25:
            df_raw = generate_synthetic_stock_data(req.symbol, days=250)
            
        res = run_volume_backtest(
            df=df_raw,
            volume_multiplier=req.volumeMultiplier,
            holding_days=req.holdingDays,
            stop_loss_pct=req.stopLossPct,
            take_profit_pct=req.takeProfitPct,
            initial_capital=req.initialCapital
        )
        return res
    except Exception as e:
        logger.error(f"Backtest error for {req.symbol}: {e}")
        df_raw = generate_synthetic_stock_data(req.symbol, days=250)
        return run_volume_backtest(
            df=df_raw,
            volume_multiplier=req.volumeMultiplier,
            holding_days=req.holdingDays,
            stop_loss_pct=req.stopLossPct,
            take_profit_pct=req.takeProfitPct,
            initial_capital=req.initialCapital
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
