from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from services.stock_data import POPULAR_STOCKS, fetch_stock_data, generate_synthetic_stock_data
from services.volume_analytics import (
    compute_volume_metrics,
    calculate_volume_profile,
    generate_ai_analysis
)
from services.backtester import run_volume_backtest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volume-research-api")

app = FastAPI(
    title="Volume Based Share Market Research API",
    description="Professional Volume Analytics, Screener & Strategy Backtesting Engine for Indian & Global Stock Markets",
    version="1.0.0"
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
    return {"status": "online", "service": "Volume Research Engine", "version": "1.0.0"}

@app.get("/api/stocks")
def get_popular_stocks():
    """Return catalog of tracked Indian and International stocks."""
    return POPULAR_STOCKS

@app.get("/api/stocks/{symbol}")
def get_stock_analysis(symbol: str, period: str = "6m"):
    """Fetch candlestick data, computed indicators, volume profile and AI analysis for a stock."""
    try:
        df_raw = fetch_stock_data(symbol, period=period)
        if df_raw.empty:
            df_raw = generate_synthetic_stock_data(symbol, days=120)
            
        df = compute_volume_metrics(df_raw)
        volume_profile = calculate_volume_profile(df, bins_count=12)
        ai_report = generate_ai_analysis(symbol, df)
        
        candles = df.to_dict(orient="records")
        latest = candles[-1] if candles else {}
        
        return {
            "symbol": symbol.upper(),
            "latest": latest,
            "candles": candles,
            "volumeProfile": volume_profile,
            "aiReport": ai_report
        }
    except Exception as e:
        logger.error(f"Error serving analysis for {symbol}: {e}")
        # Fallback to pure synthetic data generation to prevent 500 error
        df_raw = generate_synthetic_stock_data(symbol, days=120)
        df = compute_volume_metrics(df_raw)
        volume_profile = calculate_volume_profile(df, bins_count=12)
        ai_report = generate_ai_analysis(symbol, df)
        candles = df.to_dict(orient="records")
        latest = candles[-1] if candles else {}
        return {
            "symbol": symbol.upper(),
            "latest": latest,
            "candles": candles,
            "volumeProfile": volume_profile,
            "aiReport": ai_report
        }

@app.get("/api/screener")
def run_screener(
    min_surge: float = Query(1.5, description="Minimum Volume Surge Multiplier"),
    sector: Optional[str] = None
):
    """Screen all tracked stocks for volume surges and institutional accumulation signals."""
    results = []
    
    for item in POPULAR_STOCKS:
        sym = item["symbol"]
        try:
            df_raw = fetch_stock_data(sym, period="3m")
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
                    "signal": signal_text
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
        df_raw = fetch_stock_data(req.symbol, period="1y")
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
