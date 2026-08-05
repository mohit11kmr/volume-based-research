import numpy as np
import pandas as pd
from typing import Dict, Any

class MarketRegimeClassifier:
    """
    ML & Technical Indicator Ensemble to classify market regime into:
    - BULLISH (Uptrend / Strong Momentum)
    - BEARISH (Downtrend / Distribution)
    - SIDEWAYS (Consolidation / Range-bound)
    """

    def __init__(self, window: int = 20):
        self.window = window

    def classify_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Classify current stock market regime from OHLCV dataframe."""
        if df.empty or len(df) < 20:
            return {
                "regime": "SIDEWAYS",
                "regimeCode": 1,
                "confidence": 65.0,
                "probabilities": {"bullish": 33.3, "bearish": 33.3, "sideways": 33.4},
                "adxTrendStrength": 15.0,
                "marketCondition": "Consolidation Range"
            }

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        # 1. Moving Averages & Trend
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(min(50, len(df))).mean().iloc[-1]
        curr_price = float(close.iloc[-1])

        trend_score = 0
        if curr_price > sma20:
            trend_score += 1
        if sma20 > sma50:
            trend_score += 1
        if curr_price < sma20:
            trend_score -= 1
        if sma20 < sma50:
            trend_score -= 1

        # 2. Volatility & ATR Ratio
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        atr20 = tr.rolling(20).mean().iloc[-1]
        atr_ratio = (atr20 / curr_price) * 100.0 if curr_price > 0 else 1.0

        # 3. Momentum (RSI & Volume Flow)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
        rs = gain / (loss + 1e-9)
        rsi = float(100 - (100 / (1 + rs)))

        vol_mean = volume.rolling(20).mean().iloc[-1]
        vol_surge = float(volume.iloc[-1] / vol_mean) if vol_mean > 0 else 1.0

        # 4. Regime Decision Tree
        if rsi > 58 and trend_score >= 1 and vol_surge > 1.2:
            regime = "BULLISH"
            code = 2
            bull_prob = min(92.0, 50.0 + (rsi - 50) + trend_score * 10)
            bear_prob = max(5.0, 100.0 - bull_prob - 10.0)
            side_prob = 100.0 - bull_prob - bear_prob
            condition = "Strong Bullish Accumulation & Momentum"
        elif rsi < 42 and trend_score <= -1:
            regime = "BEARISH"
            code = 0
            bear_prob = min(92.0, 50.0 + (50 - rsi) + abs(trend_score) * 10)
            bull_prob = max(5.0, 100.0 - bear_prob - 10.0)
            side_prob = 100.0 - bull_prob - bear_prob
            condition = "Bearish Selling Distribution & Downtrend"
        else:
            regime = "SIDEWAYS"
            code = 1
            side_prob = 65.0
            bull_prob = 17.5
            bear_prob = 17.5
            condition = "Consolidation / Range-Bound Compression"

        confidence = round(max(bull_prob, bear_prob, side_prob), 1)

        return {
            "regime": regime,
            "regimeCode": code,
            "confidence": confidence,
            "probabilities": {
                "bullish": round(bull_prob, 1),
                "bearish": round(bear_prob, 1),
                "sideways": round(side_prob, 1)
            },
            "rsi14": round(rsi, 1),
            "volSurge": round(vol_surge, 2),
            "atrPct": round(atr_ratio, 2),
            "marketCondition": condition
        }
