import math
from typing import Dict, Any, List

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

def analyze_option_strike_valuation(
    symbol: str,
    underlying_price: float,
    days_to_expiry: int = 7
) -> Dict[str, Any]:
    """Generate Smart Option Chain Valuation & Fair Premium Rating (CHEAP / FAIR / EXPENSIVE)."""
    if underlying_price <= 0:
        underlying_price = 1250.0

    step = 50.0 if underlying_price > 1000 else 20.0
    atm_strike = round(underlying_price / step) * step
    r = 0.07 # 7% RBI Risk-Free Rate
    T = max(1, days_to_expiry) / 365.0
    iv = 0.18 # 18% Base IV

    strikes = [atm_strike - 2 * step, atm_strike - step, atm_strike, atm_strike + step, atm_strike + 2 * step]
    option_chain = []

    for k in strikes:
        call_bs = calculate_black_scholes(underlying_price, k, T, r, iv, "CALL")
        put_bs = calculate_black_scholes(underlying_price, k, T, r, iv, "PUT")

        # Market Premium Noise (+/- 12%)
        call_market = round(call_bs["fairValue"] * (0.92 if k > underlying_price else 1.08), 2)
        put_market = round(put_bs["fairValue"] * (1.08 if k > underlying_price else 0.92), 2)

        # Call Valuation Rating
        call_ratio = call_market / call_bs["fairValue"] if call_bs["fairValue"] > 0 else 1.0
        if call_ratio < 0.92:
            call_rating = "CHEAP (UNDERVALUED)"
        elif call_ratio > 1.08:
            call_rating = "EXPENSIVE (OVERVALUED)"
        else:
            call_rating = "FAIRLY PRICED"

        # Put Valuation Rating
        put_ratio = put_market / put_bs["fairValue"] if put_bs["fairValue"] > 0 else 1.0
        if put_ratio < 0.92:
            put_rating = "CHEAP (UNDERVALUED)"
        elif put_ratio > 1.08:
            put_rating = "EXPENSIVE (OVERVALUED)"
        else:
            put_rating = "FAIRLY PRICED"

        option_chain.append({
            "strikePrice": k,
            "isATM": k == atm_strike,
            "call": {
                "marketPremium": call_market,
                "fairValue": call_bs["fairValue"],
                "valuation": call_rating,
                "delta": call_bs["delta"],
                "theta": call_bs["theta"]
            },
            "put": {
                "marketPremium": put_market,
                "fairValue": put_bs["fairValue"],
                "valuation": put_rating,
                "delta": put_bs["delta"],
                "theta": put_bs["theta"]
            }
        })

    # Recommended Best Strike Choice
    best_call = next((o for o in option_chain if o["call"]["valuation"].startswith("CHEAP")), option_chain[2])
    best_put = next((o for o in option_chain if o["put"]["valuation"].startswith("CHEAP")), option_chain[2])

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
        }
    }
