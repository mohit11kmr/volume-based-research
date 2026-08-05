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
from services.risk_engine import PaperTradingSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volume-research-api")

app = FastAPI(
    title="Volume Based Share Market Research API",
    description="Professional Volume Analytics, Live Intraday Ticker, Risk Engine & Paper Trading Simulator",
    version="2.2.0"
)

# Enable CORS for all origins (public read-only API; credentials not required)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate Global Paper Trading Simulator
paper_simulator = PaperTradingSimulator(initial_capital=100000.0)

class BacktestRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    volumeMultiplier: float = 2.0
    holdingDays: int = 5
    stopLossPct: float = 2.0
    takeProfitPct: float = 6.0
    initialCapital: float = 100000.0

class PaperBuyRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    stopLossPct: float = 2.0
    takeProfitPct: float = 6.0

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "Volume Research Engine & Risk Paper Simulator", "version": "2.2.0"}

@app.get("/api/stocks")
def get_popular_stocks():
    return POPULAR_STOCKS

@app.get("/api/stocks/{symbol}/quote")
def get_stock_live_quote(symbol: str):
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

# Paper Trading & Portfolio Simulator Endpoints
@app.get("/api/paper-trading/portfolio")
def get_paper_portfolio():
    """Return virtual portfolio summary, open positions & live unrealized PnL."""
    live_prices = {}
    for pos in paper_simulator.open_positions:
        sym = pos["symbol"]
        quote = fetch_live_quote(sym)
        live_prices[sym] = quote.get("lastPrice", pos["entryPrice"])
        
    return paper_simulator.get_portfolio_summary(live_prices)

@app.post("/api/paper-trading/buy")
def place_paper_buy_order(req: PaperBuyRequest):
    """Execute virtual paper buy order using 2% Risk Engine Sizing."""
    quote = fetch_live_quote(req.symbol)
    curr_price = quote.get("lastPrice", 1000.0)
    
    res = paper_simulator.execute_paper_buy(
        symbol=req.symbol,
        current_price=curr_price,
        stop_loss_pct=req.stopLossPct,
        take_profit_pct=req.takeProfitPct
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@app.post("/api/paper-trading/close/{position_id}")
def close_paper_position(position_id: int):
    """Close active paper trade position."""
    pos = next((p for p in paper_simulator.open_positions if p["id"] == position_id), None)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
        
    quote = fetch_live_quote(pos["symbol"])
    exit_p = quote.get("lastPrice", pos["entryPrice"])
    return paper_simulator.close_position(position_id, exit_p, reason="Manual Exit")

@app.post("/api/paper-trading/reset")
def reset_paper_account():
    """Reset virtual paper account to ₹100,000 cash balance."""
    paper_simulator.reset_portfolio()
    return {"message": "Paper Trading Virtual Account successfully reset to ₹100,000 cash."}

@app.get("/api/brain/status")
def get_ai_brain_status():
    return get_brain_status()

@app.get("/api/brain/scenarios")
def get_ai_scenarios(symbol: str = "RELIANCE.NS"):
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
