import math
import logging
from typing import Dict, Any, List

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

def norm_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal distribution."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def calculate_black_scholes(
    S: float,       # Underlying Spot Price
    K: float,       # Strike Price
    T: float,       # Time to expiry in years (e.g. 7 days / 365)
    r: float,       # Risk-free interest rate (e.g. 0.07)
    sigma: float,   # Implied Volatility (e.g. 0.18)
    option_type: str = "CALL"
) -> Dict[str, float]:
    """Calculate Black-Scholes Option Fair Value and Greeks (Delta, Gamma, Theta, Vega)."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        intrinsic = max(0.0, S - K) if option_type.upper() == "CALL" else max(0.0, K - S)
        return {"fairValue": round(intrinsic, 2), "delta": 0.5, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    pdf_d1 = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * d1 ** 2)

    if option_type.upper() == "CALL":
        fair_value = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        delta = norm_cdf(d1)
    else:
        fair_value = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
        delta = norm_cdf(d1) - 1.0

    gamma = pdf_d1 / (S * sigma * math.sqrt(T))
    vega = (S * pdf_d1 * math.sqrt(T)) / 100.0
    theta = (- (S * pdf_d1 * sigma) / (2.0 * math.sqrt(T))) / 365.0

    return {
        "fairValue": round(max(0.05, fair_value), 2),
        "delta": round(delta, 3),
        "gamma": round(gamma, 4),
        "theta": round(theta, 2),
        "vega": round(vega, 2)
    }

def _fetch_real_option_chain(symbol: str, underlying_price: float, days_to_expiry: int):
    """Fetch nearest real option chain from yfinance. Returns (chain_df, expiry, iv) or None."""
    if not YFINANCE_AVAILABLE:
        return None
    try:
        ticker = yf.Ticker(symbol)
        expiries = list(ticker.options)
        if not expiries:
            return None
        expiry = expiries[0]
        chain = ticker.option_chain(expiry)
        if chain.calls is None or chain.calls.empty:
            return None
        # Filter strikes near ATM (+/- 2 steps)
        step = 50.0 if underlying_price > 1000 else 20.0
        atm_strike = round(underlying_price / step) * step
        strikes = sorted({int(k) for k in chain.calls["strike"] if abs(k - underlying_price) <= step * 2.5})
        strikes = strikes[:10]
        if not strikes:
            return None
        return chain, expiry, strikes, atm_strike
    except Exception as e:
        logger.warning(f"Real option chain fetch failed for {symbol}: {e}")
        return None

def _rate_premium(market: float, fair: float) -> str:
    if fair <= 0:
        return "FAIRLY PRICED"
    ratio = market / fair
    if ratio < 0.92:
        return "CHEAP (UNDERVALUED)"
    if ratio > 1.08:
        return "EXPENSIVE (OVERVALUED)"
    return "FAIRLY PRICED"

def _market_mid(row, side: str) -> float:
    bid = row.get("bid")
    ask = row.get("ask")
    if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
        return round((float(bid) + float(ask)) / 2.0, 2)
    last = row.get("lastPrice")
    return round(float(last), 2) if isinstance(last, (int, float)) and last > 0 else 0.0

def analyze_option_strike_valuation(
    symbol: str,
    underlying_price: float,
    days_to_expiry: int = 7
) -> Dict[str, Any]:
    """Generate Option Chain Valuation & Fair Premium Rating (CHEAP / FAIR / EXPENSIVE)."""
    if underlying_price <= 0:
        underlying_price = 1250.0

    step = 50.0 if underlying_price > 1000 else 20.0
    atm_strike = round(underlying_price / step) * step
    r = 0.07 # 7% RBI Risk-Free Rate
    T = max(1, days_to_expiry) / 365.0
    iv = 0.18 # 18% Base IV

    real = _fetch_real_option_chain(symbol, underlying_price, days_to_expiry)
    option_chain = []

    if real:
        chain, expiry, strikes, real_atm = real
        atm_strike = real_atm
        calls = chain.calls.set_index("strike")
        puts = chain.puts.set_index("strike")
        for k in strikes:
            if k not in calls.index:
                continue
            call_row = calls.loc[k]
            put_row = puts.loc[k] if k in puts.index else {}

            call_iv = call_row.get("impliedVolatility")
            put_iv = put_row.get("impliedVolatility")
            call_bs = calculate_black_scholes(underlying_price, k, T, r, float(call_iv) if isinstance(call_iv, (int, float)) and call_iv > 0 else iv, "CALL")
            put_bs = calculate_black_scholes(underlying_price, k, T, r, float(put_iv) if isinstance(put_iv, (int, float)) and put_iv > 0 else iv, "PUT")

            call_market = _market_mid(call_row, "call")
            put_market = _market_mid(put_row, "put")
            if call_market <= 0:
                call_market = round(call_bs["fairValue"] * (0.92 if k > underlying_price else 1.08), 2)
            if put_market <= 0:
                put_market = round(put_bs["fairValue"] * (1.08 if k > underlying_price else 0.92), 2)

            option_chain.append({
                "strikePrice": k,
                "isATM": k == atm_strike,
                "call": {
                    "marketPremium": call_market,
                    "fairValue": call_bs["fairValue"],
                    "valuation": _rate_premium(call_market, call_bs["fairValue"]),
                    "delta": call_bs["delta"],
                    "theta": call_bs["theta"]
                },
                "put": {
                    "marketPremium": put_market,
                    "fairValue": put_bs["fairValue"],
                    "valuation": _rate_premium(put_market, put_bs["fairValue"]),
                    "delta": put_bs["delta"],
                    "theta": put_bs["theta"]
                }
            })
    else:
        strikes = [atm_strike - 2 * step, atm_strike - step, atm_strike, atm_strike + step, atm_strike + 2 * step]
        for k in strikes:
            call_bs = calculate_black_scholes(underlying_price, k, T, r, iv, "CALL")
            put_bs = calculate_black_scholes(underlying_price, k, T, r, iv, "PUT")

            # Fallback market premium noise (+/- 12%) only used when no real chain exists
            call_market = round(call_bs["fairValue"] * (0.92 if k > underlying_price else 1.08), 2)
            put_market = round(put_bs["fairValue"] * (1.08 if k > underlying_price else 0.92), 2)

            option_chain.append({
                "strikePrice": k,
                "isATM": k == atm_strike,
                "call": {
                    "marketPremium": call_market,
                    "fairValue": call_bs["fairValue"],
                    "valuation": _rate_premium(call_market, call_bs["fairValue"]),
                    "delta": call_bs["delta"],
                    "theta": call_bs["theta"]
                },
                "put": {
                    "marketPremium": put_market,
                    "fairValue": put_bs["fairValue"],
                    "valuation": _rate_premium(put_market, put_bs["fairValue"]),
                    "delta": put_bs["delta"],
                    "theta": put_bs["theta"]
                }
            })

    if not option_chain:
        return {"symbol": symbol.upper(), "error": "No option chain available for this symbol."}

    best_call = next((o for o in option_chain if o["call"]["valuation"].startswith("CHEAP")), option_chain[len(option_chain)//2])
    best_put = next((o for o in option_chain if o["put"]["valuation"].startswith("CHEAP")), option_chain[len(option_chain)//2])

    return {
        "symbol": symbol.upper(),
        "underlyingPrice": round(underlying_price, 2),
        "daysToExpiry": days_to_expiry,
        "impliedVolatilityPct": round(iv * 100.0, 1),
        "atmStrike": atm_strike,
        "optionChain": option_chain,
        "recommendation": {
            "bestCallStrike": best_call["strikePrice"],
            "bestCallValuation": best_call["call"]["valuation"],
            "bestPutStrike": best_put["strikePrice"],
            "bestPutValuation": best_put["put"]["valuation"]
        },
        "isRealData": real is not None,
        "dataSource": "LIVE OPTION CHAIN" if real else "BLACK-SCHOLES ESTIMATE",
        "expiryDate": real[1] if real else None
    }
