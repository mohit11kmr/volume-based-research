import pandas as pd
import numpy as np
from typing import Dict, Any, List
from services.regime_classifier import MarketRegimeClassifier

regime_classifier = MarketRegimeClassifier()

def compute_volume_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Volume Surge Ratio, OBV, VWAP, CMF, and Price Changes."""
    if df.empty or len(df) < 2:
        return df

    df = df.copy()
    
    # 20-Day SMA Volume & Surge Ratio
    df["Vol_SMA20"] = df["Volume"].rolling(window=min(20, len(df)), min_periods=1).mean()
    df["Vol_Surge_Ratio"] = np.where(
        df["Vol_SMA20"] > 0,
        np.round(df["Volume"] / df["Vol_SMA20"], 2),
        1.0
    )
    
    # On-Balance Volume (OBV)
    obv = [0.0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
            
    df["OBV"] = obv
    df["OBV_EMA20"] = df["OBV"].ewm(span=min(20, len(df)), adjust=False).mean()
    
    # Volume Weighted Average Price (VWAP)
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    tp_vol = typical_price * df["Volume"]
    df["VWAP"] = np.round(tp_vol.cumsum() / np.maximum(1, df["Volume"].cumsum()), 2)
    
    # Chaikin Money Flow (CMF 20)
    mf_multiplier = np.where(
        (df["High"] - df["Low"]) > 0,
        ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]),
        0.0
    )
    mf_volume = mf_multiplier * df["Volume"]
    cmf_sum_vol = df["Volume"].rolling(window=min(20, len(df)), min_periods=1).sum()
    df["CMF"] = np.where(
        cmf_sum_vol > 0,
        np.round(mf_volume.rolling(window=min(20, len(df)), min_periods=1).sum() / cmf_sum_vol, 3),
        0.0
    )
    
    # Price Change Pct
    df["Price_Change_Pct"] = np.round(df["Close"].pct_change().fillna(0.0) * 100.0, 2)
    
    # Signal Text
    df["Volume_Signal"] = np.where(
        (df["Vol_Surge_Ratio"] >= 2.0) & (df["Price_Change_Pct"] > 0),
        "BULLISH BREAKOUT",
        np.where(
            (df["Vol_Surge_Ratio"] >= 2.0) & (df["Price_Change_Pct"] < 0),
            "BEARISH DISTRIBUTION",
            "NEUTRAL / CONSOLIDATION"
        )
    )
    
    return df

def calculate_volume_profile(df: pd.DataFrame, bins_count: int = 12) -> List[Dict[str, Any]]:
    """Compute Price-wise Volume Profile and Point of Control (POC)."""
    if df.empty or len(df) < 2:
        return []

    min_p = float(df["Low"].min())
    max_p = float(df["High"].max())
    
    if min_p == max_p:
        return [{"priceRange": f"₹{min_p:.2f}", "volume": int(df["Volume"].sum()), "isPOC": True}]
        
    bins = np.linspace(min_p, max_p, bins_count + 1)
    profile = []
    max_vol = -1
    poc_idx = -1
    
    for i in range(bins_count):
        p_low = bins[i]
        p_high = bins[i + 1]
        mask = (df["Close"] >= p_low) & (df["Close"] <= p_high)
        vol_sum = int(df.loc[mask, "Volume"].sum())
        
        if vol_sum > max_vol:
            max_vol = vol_sum
            poc_idx = i
            
        profile.append({
            "priceLow": round(p_low, 2),
            "priceHigh": round(p_high, 2),
            "priceRange": f"₹{p_low:.1f} - ₹{p_high:.1f}",
            "volume": vol_sum,
            "isPOC": False
        })
        
    if poc_idx >= 0 and poc_idx < len(profile):
        profile[poc_idx]["isPOC"] = True
        
    return profile

def generate_ai_analysis(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Generate AI market report incorporating Market Regime Classifier."""
    if df.empty:
        return {
            "symbol": symbol,
            "summary": "No data available.",
            "recommendation": "NEUTRAL",
            "keyLevels": {"support": 0, "resistance": 0, "poc": 0},
            "marketRegime": {"regime": "SIDEWAYS", "confidence": 50.0}
        }

    latest = df.iloc[-1]
    vol_surge = float(latest.get("Vol_Surge_Ratio", 1.0))
    cmf_val = float(latest.get("CMF", 0.0))
    price_chg = float(latest.get("Price_Change_Pct", 0.0))
    close_p = float(latest.get("Close", 0.0))
    obv_val = float(latest.get("OBV", 0.0))
    obv_ema = float(latest.get("OBV_EMA20", 0.0))
    vwap_val = float(latest.get("VWAP", 0.0))

    regime_info = regime_classifier.classify_regime(df)

    # Key Levels
    supp = round(float(df["Low"].tail(20).min()), 2)
    resist = round(float(df["High"].tail(20).max()), 2)

    # Bullish / Bearish Score
    score = 0
    if vol_surge >= 2.0: score += 2
    if cmf_val > 0.1: score += 2
    if obv_val > obv_ema: score += 1
    if close_p > vwap_val: score += 1
    if regime_info["regime"] == "BULLISH": score += 2

    if score >= 5:
        recommendation = "STRONG BUY (Institutional Surge)"
        summary = f"{symbol} exhibits massive institutional volume accumulation ({vol_surge}x 20-day SMA). Market regime is {regime_info['regime']} with CMF at +{cmf_val}."
    elif score >= 3:
        recommendation = "BUY ON DIPS"
        summary = f"{symbol} shows positive money flow (CMF: +{cmf_val}) above VWAP ₹{vwap_val}. Market regime is {regime_info['regime']}."
    elif score <= 1 and price_chg < -1.5:
        recommendation = "BEARISH AVOID / SHORT"
        summary = f"{symbol} experiencing heavy selling pressure with negative money flow (CMF: {cmf_val})."
    else:
        recommendation = "NEUTRAL / HOLD"
        summary = f"{symbol} is consolidating near VWAP ₹{vwap_val}. Market regime is {regime_info['regime']}."

    return {
        "symbol": symbol,
        "summary": summary,
        "recommendation": recommendation,
        "marketRegime": regime_info,
        "keyLevels": {
            "support": supp,
            "resistance": resist,
            "vwap": vwap_val
        }
    }
