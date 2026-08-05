import pandas as pd
import numpy as np
from typing import Dict, Any, List

def compute_volume_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all advanced volume indicators on the stock DataFrame."""
    df = df.copy()
    
    # 1. 20-period Volume Simple Moving Average (SMA)
    df["Vol_SMA20"] = df["Volume"].rolling(window=20, min_periods=1).mean().fillna(0.0)
    
    # Avoid division by zero
    vol_sma_safe = df["Vol_SMA20"].replace(0, 1.0)
    df["Vol_Surge_Ratio"] = (df["Volume"] / vol_sma_safe).round(2).fillna(1.0)
    
    # 2. Price Change & Price Trend
    df["Price_Change"] = df["Close"].diff().fillna(0.0).round(2)
    df["Price_Change_Pct"] = (df["Close"].pct_change().fillna(0.0) * 100.0).round(2)
    
    # 3. OBV (On-Balance Volume)
    obv = [0.0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i-1]:
            obv.append(float(obv[-1] + df["Volume"].iloc[i]))
        elif df["Close"].iloc[i] < df["Close"].iloc[i-1]:
            obv.append(float(obv[-1] - df["Volume"].iloc[i]))
        else:
            obv.append(float(obv[-1]))
    df["OBV"] = obv
    df["OBV_EMA20"] = df["OBV"].ewm(span=20, adjust=False).mean().round(0).fillna(0.0)
    
    # 4. VWAP (Volume Weighted Average Price)
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    df["Cum_TP_Vol"] = (typical_price * df["Volume"]).cumsum()
    df["Cum_Vol"] = df["Volume"].cumsum().replace(0, 1.0)
    df["VWAP"] = (df["Cum_TP_Vol"] / df["Cum_Vol"]).round(2).fillna(0.0)
    
    # 5. Chaikin Money Flow (CMF 20-period)
    high_low_diff = (df["High"] - df["Low"]).replace(0, 0.0001)
    mf_multiplier = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / high_low_diff
    mf_volume = mf_multiplier * df["Volume"]
    
    vol_sum_20 = df["Volume"].rolling(window=20, min_periods=1).sum().replace(0, 1.0)
    df["CMF"] = (mf_volume.rolling(window=20, min_periods=1).sum() / vol_sum_20).round(3).fillna(0.0)
    
    # 6. Accumulation vs Distribution Signal
    def classify_candle(row):
        vol_ratio = float(row["Vol_Surge_Ratio"])
        p_pct = float(row["Price_Change_Pct"])
        if vol_ratio >= 1.8 and p_pct > 0.5:
            return "Institutional Accumulation (Bullish)"
        elif vol_ratio >= 1.8 and p_pct < -0.5:
            return "Institutional Distribution (Bearish)"
        elif vol_ratio >= 1.5:
            return "High Volume Spike"
        else:
            return "Normal Volume"
            
    df["Volume_Signal"] = df.apply(classify_candle, axis=1)
    df = df.fillna(0.0)
    return df

def calculate_volume_profile(df: pd.DataFrame, bins_count: int = 15) -> List[Dict[str, Any]]:
    """Compute Price-wise Volume Profile and Point of Control (POC)."""
    if df.empty:
        return []
        
    min_p = float(df["Low"].min())
    max_p = float(df["High"].max())
    
    if min_p == max_p:
        max_p += 1.0
        
    bins = np.linspace(min_p, max_p, bins_count + 1)
    profile = []
    
    for i in range(bins_count):
        p_low = float(bins[i])
        p_high = float(bins[i+1])
        
        mask = (df["Low"] <= p_high) & (df["High"] >= p_low)
        subset = df[mask]
        
        buy_vol = float(subset[subset["Close"] >= subset["Open"]]["Volume"].sum())
        sell_vol = float(subset[subset["Close"] < subset["Open"]]["Volume"].sum())
        total_vol = buy_vol + sell_vol
        
        profile.append({
            "priceRange": f"{round(p_low, 1)} - {round(p_high, 1)}",
            "priceLevel": float(round((p_low + p_high) / 2.0, 2)),
            "totalVolume": int(total_vol),
            "buyVolume": int(buy_vol),
            "sellVolume": int(sell_vol)
        })
        
    if profile:
        poc_bin = max(profile, key=lambda x: x["totalVolume"])
        for p in profile:
            p["isPOC"] = bool(p["priceLevel"] == poc_bin["priceLevel"])
            
    return profile

def generate_ai_analysis(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Generate smart algorithmic insights based on recent volume and price behavior."""
    if len(df) < 5:
        return {"summary": "Insufficient data for volume analysis."}
        
    latest = df.iloc[-1]
    prev_5 = df.iloc[-5:]
    avg_vol_20 = float(latest["Vol_SMA20"])
    surge_ratio = float(latest["Vol_Surge_Ratio"])
    cmf = float(latest["CMF"])
    obv_trend = "RISING" if float(latest["OBV"]) > float(latest["OBV_EMA20"]) else "FALLING"
    
    bullish_candles = int((prev_5["Price_Change_Pct"] > 0).sum())
    volume_surge_days = int((prev_5["Vol_Surge_Ratio"] > 1.5).sum())
    
    insights = []
    
    if surge_ratio >= 2.5:
        insights.append(f"🔥 **Massive Volume Spike**: Trading at **{surge_ratio}x** its 20-day average volume today.")
    elif surge_ratio >= 1.5:
        insights.append(f"⚡ **Elevated Volume**: Trading volume is **{surge_ratio}x** normal levels.")
    else:
        insights.append(f"📊 Volume is trading within normal historical bounds (**{surge_ratio}x** SMA20).")
        
    if cmf > 0.15:
        insights.append(f"💚 **Strong Buying Inflow (CMF = {cmf})**: Money flow indicates continuous institutional accumulation.")
    elif cmf < -0.15:
        insights.append(f"🔴 **Selling Outflow (CMF = {cmf})**: Capital is flowing out of the asset.")
    else:
        insights.append(f"⚖️ Neutral money flow (CMF = {cmf}).")
        
    if obv_trend == "RISING":
        insights.append(f"📈 **OBV Uptrend**: On-Balance Volume is above its 20 EMA, confirming bullish volume pressure.")
    else:
        insights.append(f"📉 **OBV Downtrend**: On-Balance Volume is lagging below its 20 EMA.")
        
    if surge_ratio >= 1.8 and float(latest["Price_Change_Pct"]) > 0 and cmf > 0:
        signal = "BULLISH BREAKOUT ACCUMULATION"
        confidence = "HIGH (88%)"
    elif surge_ratio >= 1.8 and float(latest["Price_Change_Pct"]) < 0:
        signal = "BEARISH DISTRIBUTION BREAKDOWN"
        confidence = "HIGH (82%)"
    elif obv_trend == "RISING" and cmf > 0:
        signal = "STEADY ACCUMULATION"
        confidence = "MEDIUM (70%)"
    else:
        signal = "NEUTRAL / CONSOLIDATION"
        confidence = "MODERATE (55%)"
        
    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "volumeSurgeRatio": surge_ratio,
        "cmf": cmf,
        "obvTrend": obv_trend,
        "volumeSurgeDaysLast5": volume_surge_days,
        "keyInsights": insights
    }
