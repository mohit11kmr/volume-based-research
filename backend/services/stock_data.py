import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

NIFTY50_STOCKS = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy / Conglomerate", "exchange": "NSE"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom", "exchange": "NSE"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure", "exchange": "NSE"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Conglomerate", "exchange": "NSE"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports & SEZ", "sector": "Infrastructure", "exchange": "NSE"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "sector": "Healthcare", "exchange": "NSE"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer Goods", "exchange": "NSE"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "sector": "Pharmaceuticals", "exchange": "NSE"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Energy / Mining", "exchange": "NSE"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "sector": "Pharmaceuticals", "exchange": "NSE"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Labs", "sector": "Pharmaceuticals", "exchange": "NSE"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "sector": "Cement / Textiles", "exchange": "NSE"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "sector": "Insurance", "exchange": "NSE"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "sector": "Metals & Mining", "exchange": "NSE"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Metals & Mining", "exchange": "NSE"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "sector": "Energy / Power", "exchange": "NSE"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Energy / Power", "exchange": "NSE"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "sector": "Insurance", "exchange": "NSE"},
    {"symbol": "SHRIRAMFIN.NS", "name": "Shriram Finance", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceuticals", "sector": "Pharmaceuticals", "exchange": "NSE"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metals & Mining", "exchange": "NSE"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer Goods", "exchange": "NSE"},
    {"symbol": "TRENT.NS", "name": "Trent Limited", "sector": "Retail", "exchange": "NSE"},
    {"symbol": "ULTRACEMCO.NS", "name": "Ultratech Cement", "sector": "Cement", "exchange": "NSE"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "ZOMATO.NS", "name": "Zomato Limited", "sector": "Internet / F&B", "exchange": "NSE"},
]

US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "US Tech", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "US Tech & AI", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "US Auto & Tech", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corp", "sector": "US Tech", "exchange": "NASDAQ"}
]

POPULAR_STOCKS = NIFTY50_STOCKS + US_STOCKS

def generate_synthetic_stock_data(symbol: str, days: int = 150, interval: str = "1d") -> pd.DataFrame:
    """Fallback generator for stock price & volume when live data fetch fails."""
    seed_val = abs(hash(symbol)) % 10000
    np.random.seed(seed_val)
    end_date = datetime.now()
    
    if interval in ["1m", "5m", "15m"]:
        # Generate Intraday Minutes candles
        candles_count = 75 if interval == "5m" else 150
        dates = [end_date - timedelta(minutes=i*5) for i in range(candles_count)]
        dates.reverse()
        date_format = "%H:%M"
    else:
        # Daily / Weekly candles
        dates = [end_date - timedelta(days=i) for i in range(days)]
        dates.reverse()
        dates = [d for d in dates if d.weekday() < 5]
        date_format = "%Y-%m-%d"
        
    n = len(dates)
    base_price = 100.0 + float(seed_val % 2500)
    returns = np.random.normal(0.0002, 0.008 if "m" in interval else 0.02, n)
    
    spike_indices = np.random.choice(n, size=max(1, int(n * 0.1)), replace=False)
    for idx in spike_indices:
        returns[idx] += float(np.random.choice([0.015, -0.012]))
        
    prices = base_price * np.exp(np.cumsum(returns))
    base_vol = (50000 if "m" in interval else 500000) + (seed_val % 500000)
    
    df_list = []
    for i in range(n):
        close_p = float(prices[i])
        high_p = close_p * (1.0 + abs(float(np.random.normal(0, 0.005 if "m" in interval else 0.01))))
        low_p = close_p * (1.0 - abs(float(np.random.normal(0, 0.005 if "m" in interval else 0.01))))
        open_p = low_p + float(np.random.uniform(0, max(0.01, high_p - low_p)))
        
        vol = int(base_vol * float(np.random.uniform(2.5, 4.2))) if i in spike_indices else int(base_vol * float(np.random.uniform(0.6, 1.4)))
            
        df_list.append({
            "Date": dates[i].strftime(date_format),
            "Open": round(open_p, 2),
            "High": round(high_p, 2),
            "Low": round(low_p, 2),
            "Close": round(close_p, 2),
            "Volume": vol
        })
        
    df = pd.DataFrame(df_list)
    df.attrs["dataSource"] = "synthetic"
    return df

def fetch_stock_data(symbol: str, period: str = "6m", interval: str = "1d") -> pd.DataFrame:
    """Fetch real-time live intraday or deep historical OHLCV data."""
    clean_symbol = symbol.strip().upper()
    
    if YFINANCE_AVAILABLE:
        try:
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty and len(df) >= 3:
                df = df.reset_index()
                date_col = None
                for col in df.columns:
                    if "date" in str(col).lower() or "time" in str(col).lower():
                        date_col = col
                        break
                        
                date_fmt = "%H:%M" if interval in ["1m", "5m", "15m"] else "%Y-%m-%d"
                
                if date_col:
                    parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
                    df["Date"] = parsed_dates.dt.strftime(date_fmt).fillna(datetime.now().strftime(date_fmt))
                else:
                    df["Date"] = [datetime.now().strftime(date_fmt)] * len(df)
                    
                for req_col in ["Open", "High", "Low", "Close", "Volume"]:
                    if req_col not in df.columns:
                        df[req_col] = 0.0
                    df[req_col] = pd.to_numeric(df[req_col], errors="coerce").fillna(0.0)
                    
                df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
                df = df.fillna(0.0)
                df.attrs["dataSource"] = "yfinance"
                return df
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {clean_symbol} (period={period}, interval={interval}): {e}")
            
    days_cnt = 365 if period in ["1y", "2y", "5y"] else 120
    return generate_synthetic_stock_data(clean_symbol, days=days_cnt, interval=interval)

def _is_market_open(now: datetime) -> bool:
    """Indian market hours: Mon-Fri 9:15 to 15:30 IST."""
    is_weekday = now.weekday() < 5
    return is_weekday and ((now.hour == 9 and now.minute >= 15) or (now.hour > 9 and now.hour < 15) or (now.hour == 15 and now.minute <= 30))


def _fetch_nse_direct_quote(symbol: str) -> Dict[str, Any]:
    """Fetch a real-time quote from NSE India's public API (for NSE symbols).

    Returns None when NSE is unreachable or the symbol is not an NSE equity.
    """
    if not symbol.endswith(".NS"):
        return None
    base_symbol = symbol.replace(".NS", "")
    try:
        import requests
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
        }
        session.get("https://www.nseindia.com", headers=headers, timeout=6)
        r = session.get(
            f"https://www.nseindia.com/api/quote-equity?symbol={base_symbol}",
            headers=headers,
            timeout=8
        )
        r.raise_for_status()
        data = r.json()
        price_info = data.get("priceInfo", {})
        last_price = price_info.get("lastPrice")
        if not last_price:
            return None
        now = datetime.now()
        return {
            "symbol": symbol.upper(),
            "lastPrice": round(float(last_price), 2),
            "priceChange": round(float(price_info.get("change", 0.0)), 2),
            "priceChangePct": round(float(price_info.get("pChange", 0.0)), 2),
            "dayHigh": round(float(price_info.get("intraDayHighLow", {}).get("max", 0.0)), 2),
            "dayLow": round(float(price_info.get("intraDayHighLow", {}).get("min", 0.0)), 2),
            "volume": int(float(price_info.get("totalTradedVolume", 0) or 0)),
            "totalDayVolume": int(float(price_info.get("totalTradedVolume", 0) or 0)),
            "marketStatus": "LIVE OPEN" if _is_market_open(now) else "CLOSED / AFTER HOURS",
            "lastUpdated": now.strftime("%H:%M:%S IST"),
            "dataSource": "nse-direct"
        }
    except Exception as e:
        logger.debug(f"NSE direct quote failed for {symbol}: {e}")
        return None


def fetch_live_quote(symbol: str) -> Dict[str, Any]:
    """Fetch instant live quote ticker details (LTP, Change %, Volume, Market Status).

    Source priority: NSE Direct API -> yfinance fast_info -> yfinance history -> synthetic.
    """
    clean_symbol = symbol.strip().upper()
    now = datetime.now()

    # 1. NSE India public API (real-time, best for .NS symbols)
    nse_quote = _fetch_nse_direct_quote(clean_symbol)
    if nse_quote is not None:
        return nse_quote

    # 2. yfinance fast_info for real-time quote data
    if YFINANCE_AVAILABLE:
        try:
            ticker = yf.Ticker(clean_symbol)
            info = ticker.fast_info
            last_price = float(info.get("lastPrice") or 0.0)
            if last_price > 0:
                prev_close = float(info.get("previousClose") or last_price)
                day_high = float(info.get("dayHigh") or 0.0)
                day_low = float(info.get("dayLow") or 0.0)
                volume = int(info.get("lastVolume") or 0)
                total_vol = int(info.get("volume") or 0)
                chg = round(last_price - prev_close, 2)
                chg_pct = round((chg / prev_close) * 100, 2) if prev_close > 0 else 0.0
                return {
                    "symbol": clean_symbol,
                    "lastPrice": round(last_price, 2),
                    "priceChange": chg,
                    "priceChangePct": chg_pct,
                    "dayHigh": round(day_high, 2),
                    "dayLow": round(day_low, 2),
                    "volume": volume,
                    "totalDayVolume": total_vol,
                    "marketStatus": "LIVE OPEN" if _is_market_open(now) else "CLOSED / AFTER HOURS",
                    "lastUpdated": now.strftime("%H:%M:%S IST"),
                    "dataSource": "yfinance"
                }
        except Exception as e:
            logger.warning(f"fast_info quote fetch failed for {clean_symbol}: {e}")

    # 3. yfinance OHLCV fallback
    df = fetch_stock_data(clean_symbol, period="1d", interval="5m")
    if df.empty:
        df = generate_synthetic_stock_data(clean_symbol, days=1, interval="5m")
        
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    close_p = float(latest["Close"])
    prev_close = float(prev["Close"]) if float(prev["Close"]) > 0 else close_p
    chg = round(close_p - prev_close, 2)
    chg_pct = round((chg / prev_close) * 100, 2) if prev_close > 0 else 0.0
    
    return {
        "symbol": clean_symbol,
        "lastPrice": close_p,
        "priceChange": chg,
        "priceChangePct": chg_pct,
        "dayHigh": float(df["High"].max()),
        "dayLow": float(df["Low"].min()),
        "volume": int(latest["Volume"]),
        "totalDayVolume": int(df["Volume"].sum()),
        "marketStatus": "LIVE OPEN" if _is_market_open(now) else "CLOSED / AFTER HOURS",
        "lastUpdated": now.strftime("%H:%M:%S IST"),
        "dataSource": df.attrs.get("dataSource", "synthetic")
    }
