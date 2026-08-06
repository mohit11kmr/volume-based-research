from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import time
import asyncio

from services.stock_data import (
    POPULAR_STOCKS,
    fetch_stock_data,
    generate_synthetic_stock_data,
    fetch_live_quote
)
from services.volume_analytics import (
    compute_volume_metrics,
    calculate_volume_profile,
    calculate_value_area,
    generate_ai_analysis
)
from services.backtester import run_volume_backtest
from services.scenario_generator import evaluate_and_rank_scenarios
from services.learning_brain import (
    get_brain_status,
    predict_ml_win_probability,
    train_brain_model
)
from services.risk_engine import PaperTradingSimulator, PaperTradingManager, _sanitize_user_id
from services.options_engine import analyze_option_strike_valuation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volume-research-api")

app = FastAPI(
    title="Volume Based Share Market Research API",
    description="Professional Volume Analytics, Options Valuation, Risk Engine & Paper Simulator",
    version="2.4.0"
)

# Enable CORS for all origins (credentials NOT allowed when origins are wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional admin token for state-mutating endpoints.
# Set ADMIN_TOKEN env var to require "X-Admin-Token" on write endpoints.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

def require_admin_token(x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token")):
    if ADMIN_TOKEN and x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing admin token")

# Thread-safe per-user paper trading registry (each browser gets isolated portfolio)
paper_manager = PaperTradingManager(initial_capital=100000.0)

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
    return {"status": "online", "service": "Volume Research Engine & Options Greeks Valuation", "version": "2.4.0"}

@app.get("/api/stocks")
def get_popular_stocks():
    return {
        "universe": "NIFTY 50 + US Tech",
        "total": len(POPULAR_STOCKS),
        "stocks": POPULAR_STOCKS
    }

@app.websocket("/ws/{symbol}")
async def ws_live_quote(websocket: WebSocket, symbol: str):
    """Stream live quotes for a symbol every 5 seconds."""
    await websocket.accept()
    try:
        while True:
            try:
                quote = fetch_live_quote(symbol)
                await websocket.send_json(quote)
            except Exception as e:
                logger.error(f"WS quote error for {symbol}: {e}")
                await websocket.send_json({"error": str(e), "symbol": symbol, "dataSource": "error"})
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=5)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for {symbol}")
    except Exception as e:
        logger.warning(f"WebSocket closed for {symbol}: {e}")

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
        value_area = calculate_value_area(volume_profile)
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
            "valueArea": value_area,
            "aiReport": ai_report,
            "mlPrediction": ml_prediction,
            "dataSource": df.attrs.get("dataSource", "unknown"),
            "isSynthetic": df.attrs.get("dataSource", "") == "synthetic"
        }
    except Exception as e:
        logger.error(f"Error serving analysis for {symbol}: {e}")
        df_raw = generate_synthetic_stock_data(symbol, days=120, interval=interval)
        df = compute_volume_metrics(df_raw)
        volume_profile = calculate_volume_profile(df, bins_count=12)
        value_area = calculate_value_area(volume_profile)
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
            "valueArea": value_area,
            "aiReport": ai_report,
            "mlPrediction": ml_prediction,
            "dataSource": "synthetic",
            "isSynthetic": True
        }

@app.get("/api/options/analysis")
def get_options_valuation(
    symbol: str = Query("RELIANCE.NS", description="Stock or Index symbol"),
    days_to_expiry: int = Query(7, description="Days to option expiry")
):
    """Return Option Chain Premium Valuation (CHEAP / FAIR / EXPENSIVE) & Greeks."""
    try:
        quote = fetch_live_quote(symbol)
        curr_price = quote.get("lastPrice", 1250.0)
        return analyze_option_strike_valuation(symbol, curr_price, days_to_expiry)
    except Exception as e:
        logger.error(f"Error serving options analysis for {symbol}: {e}")
        return analyze_option_strike_valuation(symbol, 1250.0, days_to_expiry)

# Paper Trading & Portfolio Simulator Endpoints (isolated per user via X-User-Id)
@app.get("/api/paper-trading/portfolio")
def get_paper_portfolio(x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    sim = paper_manager.get(x_user_id)
    live_prices = {}
    for pos in sim.open_positions:
        sym = pos["symbol"]
        quote = fetch_live_quote(sym)
        live_prices[sym] = quote.get("lastPrice", pos["entryPrice"])
        
    summary = sim.get_portfolio_summary(live_prices)
    summary["userId"] = "default" if not x_user_id else _sanitize_user_id(x_user_id)
    return summary

@app.post("/api/paper-trading/buy")
def place_paper_buy_order(
    req: PaperBuyRequest,
    _: None = Depends(require_admin_token),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    sim = paper_manager.get(x_user_id)
    quote = fetch_live_quote(req.symbol)
    curr_price = quote.get("lastPrice", 1000.0)
    
    res = sim.execute_paper_buy(
        symbol=req.symbol,
        current_price=curr_price,
        stop_loss_pct=req.stopLossPct,
        take_profit_pct=req.takeProfitPct
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@app.post("/api/paper-trading/close/{position_id}")
def close_paper_position(
    position_id: int,
    _: None = Depends(require_admin_token),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    sim = paper_manager.get(x_user_id)
    pos = next((p for p in sim.open_positions if p["id"] == position_id), None)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
        
    quote = fetch_live_quote(pos["symbol"])
    exit_p = quote.get("lastPrice", pos["entryPrice"])
    return sim.close_position(position_id, exit_p, reason="Manual Exit")

@app.post("/api/paper-trading/reset")
def reset_paper_account(
    _: None = Depends(require_admin_token),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    sim = paper_manager.get(x_user_id)
    sim.reset_portfolio()
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
            
        res = evaluate_and_rank_scenarios(df_raw, symbol)
        res["dataSource"] = df_raw.attrs.get("dataSource", "unknown")
        return res
    except Exception as e:
        logger.error(f"Scenario generation error for {symbol}: {e}")
        df_raw = generate_synthetic_stock_data(symbol, days=250)
        res = evaluate_and_rank_scenarios(df_raw, symbol)
        res["dataSource"] = "synthetic"
        return res

@app.post("/api/brain/optimize")
def retrain_ai_brain(_: None = Depends(require_admin_token)):
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

_SCREENER_CACHE: Dict[str, Dict[str, Any]] = {}
_SCREENER_CACHE_TTL = 120

def _screen_single_stock(item: Dict[str, str], min_surge: float) -> Optional[Dict[str, Any]]:
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
        mfi_val = float(latest.get("MFI", 50.0))
        vol_z = float(latest.get("Volume_ZScore", 0.0))
        pocket_pivot = bool(latest.get("Pocket_Pivot", False))
        close_p = float(latest["Close"])
        vol_val = int(latest["Volume"])
        signal_text = str(latest["Volume_Signal"])
        obv_trend = "RISING" if float(latest["OBV"]) > float(latest["OBV_EMA20"]) else "FALLING"
        adl_trend = "RISING" if float(latest.get("ADL", 0.0)) > float(latest.get("ADL_EMA20", 0.0)) else "FALLING"

        value_area = calculate_value_area(calculate_volume_profile(df_raw))

        ml_pred = predict_ml_win_probability(surge, cmf_val, obv_trend)

        if surge >= min_surge:
            return {
                "symbol": sym,
                "name": item["name"],
                "sector": item["sector"],
                "exchange": item["exchange"],
                "closePrice": close_p,
                "priceChangePct": price_chg,
                "volume": vol_val,
                "volumeSurgeRatio": surge,
                "volumeZScore": vol_z,
                "cmf": cmf_val,
                "mfi": mfi_val,
                "pocketPivot": pocket_pivot,
                "adlTrend": adl_trend,
                "signal": signal_text,
                "valueArea": value_area,
                "mlWinProbability": ml_pred["mlWinProbabilityPct"],
                "dataSource": df.attrs.get("dataSource", "unknown")
            }
    except Exception as e:
        logger.warning(f"Screener error processing {sym}: {e}")
    return None

@app.get("/api/screener")
def run_screener(
    min_surge: float = Query(1.5, description="Minimum Volume Surge Multiplier"),
    sector: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    force_refresh: bool = Query(False)
):
    cache_key = f"{min_surge}|{sector}"
    cached = _SCREENER_CACHE.get(cache_key)
    if cached and not force_refresh and (time.time() - cached["ts"]) < _SCREENER_CACHE_TTL:
        results = cached["results"]
        results = [r for r in results if sector is None or sector.lower() in r["sector"].lower()]
        return {
            "count": len(results),
            "minSurgeApplied": min_surge,
            "sector": sector,
            "dataSource": cached.get("dataSource"),
            "fromCache": True,
            "results": results[:limit]
        }

    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_screen_single_stock, item, min_surge) for item in POPULAR_STOCKS]
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x["volumeSurgeRatio"], reverse=True)
    if sector:
        results = [r for r in results if sector.lower() in r["sector"].lower()]

    sources = {r["dataSource"] for r in results}
    primary_source = "live" if sources == {"yfinance", "nse-direct"} or sources == {"yfinance"} or sources == {"nse-direct"} else "mixed"
    if not sources:
        primary_source = "synthetic"

    _SCREENER_CACHE[cache_key] = {
        "ts": time.time(),
        "results": results,
        "dataSource": primary_source
    }

    return {
        "count": len(results),
        "minSurgeApplied": min_surge,
        "sector": sector,
        "dataSource": primary_source,
        "fromCache": False,
        "results": results[:limit]
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
        res["dataSource"] = df_raw.attrs.get("dataSource", "unknown")
        return res
    except Exception as e:
        logger.error(f"Backtest error for {req.symbol}: {e}")
        df_raw = generate_synthetic_stock_data(req.symbol, days=250)
        res = run_volume_backtest(
            df=df_raw,
            volume_multiplier=req.volumeMultiplier,
            holding_days=req.holdingDays,
            stop_loss_pct=req.stopLossPct,
            take_profit_pct=req.takeProfitPct,
            initial_capital=req.initialCapital
        )
        res["dataSource"] = "synthetic"
        return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
