import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

# List of popular Indian (NSE) and Global tech tickers
POPULAR_STOCKS = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy / Conglomerate", "exchange": "NSE"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking & Finance", "exchange": "NSE"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom", "exchange": "NSE"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "FMCG", "exchange": "NSE"},
    {"symbol": "LTIM.NS", "name": "LTIMindtree", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "US Tech", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "US Tech & AI", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "US Auto & Tech", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corp", "sector": "US Tech", "exchange": "NASDAQ"}
]

def generate_synthetic_stock_data(symbol: str, days: int = 150) -> pd.DataFrame:
    """Fallback generator for stock price & volume when live data fetch fails."""
    np.random.seed(abs(hash(symbol)) % 10000)
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    # Filter weekends
    dates = [d for d in dates if d.weekday() < 5]
    n = len(dates)
    
    base_price = 100 + (abs(hash(symbol)) % 2500)
    returns = np.random.normal(0.0005, 0.02, n)
    
    # Inject volume spikes and price action
    spike_indices = np.random.choice(n, size=int(n * 0.1), replace=False)
    for idx in spike_indices:
        returns[idx] += np.random.choice([0.035, -0.03])
        
    prices = base_price * np.exp(np.cumsum(returns))
    
    df_list = []
    base_vol = 500000 + (abs(hash(symbol)) % 2000000)
    
    for i in range(n):
        close_p = prices[i]
        high_p = close_p * (1 + abs(np.random.normal(0, 0.01)))
        low_p = close_p * (1 - abs(np.random.normal(0, 0.01)))
        open_p = low_p + np.random.uniform(0, high_p - low_p)
        
        # Volume Spike Logic
        if i in spike_indices:
            vol = int(base_vol * np.random.uniform(2.5, 4.8))
        else:
            vol = int(base_vol * np.random.uniform(0.6, 1.4))
            
        df_list.append({
            "Date": dates[i].strftime("%Y-%m-%d"),
            "Open": round(open_p, 2),
            "High": round(high_p, 2),
            "Low": round(low_p, 2),
            "Close": round(close_p, 2),
            "Volume": vol
        })
        
    df = pd.DataFrame(df_list)
    df.set_index("Date", inplace=False)
    return df

def fetch_stock_data(symbol: str, period: str = "6m") -> pd.DataFrame:
    """Fetch historical OHLCV data for stock symbol from yfinance or fallback."""
    clean_symbol = symbol.strip().upper()
    
    if YFINANCE_AVAILABLE:
        try:
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period)
            if not df.empty and len(df) > 10:
                df = df.reset_index()
                if "Date" in df.columns:
                    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
                return df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {clean_symbol}: {e}")
            
    # Fallback synthetic realistic data generator
    return generate_synthetic_stock_data(clean_symbol, days=120)
