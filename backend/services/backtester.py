import pandas as pd
import numpy as np
from typing import Dict, Any, List

def run_volume_backtest(
    df: pd.DataFrame,
    volume_multiplier: float = 2.0,
    holding_days: int = 5,
    stop_loss_pct: float = 2.0,
    take_profit_pct: float = 6.0,
    initial_capital: float = 100000.0
) -> Dict[str, Any]:
    """Execute historical strategy backtest based on volume surge breakouts."""
    if len(df) < 25:
        return {"error": "Not enough historical data for backtesting."}
        
    df = df.copy()
    df["SMA20_Close"] = df["Close"].rolling(20).mean()
    df["Vol_SMA20"] = df["Volume"].rolling(20).mean()
    
    capital = initial_capital
    equity_curve = []
    trades = []
    in_trade = False
    entry_price = 0.0
    entry_date = ""
    target_price = 0.0
    stop_price = 0.0
    hold_count = 0
    shares = 0
    
    for i in range(20, len(df)):
        row = df.iloc[i]
        curr_date = row["Date"]
        close_p = row["Close"]
        high_p = row["High"]
        low_p = row["Low"]
        vol = row["Volume"]
        vol_sma = row["Vol_SMA20"]
        sma_close = row["SMA20_Close"]
        
        # 1. Manage active position
        if in_trade:
            hold_count += 1
            exit_trade = False
            exit_reason = ""
            exit_price = close_p
            
            # Check Stop Loss
            if low_p <= stop_price:
                exit_trade = True
                exit_price = stop_price
                exit_reason = "Stop Loss Hit"
            # Check Take Profit
            elif high_p >= target_price:
                exit_trade = True
                exit_price = target_price
                exit_reason = "Take Profit Hit"
            # Check Max Holding Period
            elif hold_count >= holding_days:
                exit_trade = True
                exit_price = close_p
                exit_reason = "Time Exit"
                
            if exit_trade:
                pnl = (exit_price - entry_price) * shares
                capital += pnl
                pnl_pct = round(((exit_price - entry_price) / entry_price) * 100, 2)
                trades.append({
                    "entryDate": entry_date,
                    "exitDate": curr_date,
                    "entryPrice": round(entry_price, 2),
                    "exitPrice": round(exit_price, 2),
                    "pnl": round(pnl, 2),
                    "pnlPct": pnl_pct,
                    "reason": exit_reason,
                    "win": pnl > 0
                })
                in_trade = False
                
        # 2. Check for entry condition if not in trade
        if not in_trade and vol_sma > 0:
            vol_ratio = vol / vol_sma
            # Buy signal: Volume Surge > multiplier AND Price above 20 SMA
            if vol_ratio >= volume_multiplier and close_p > sma_close:
                in_trade = True
                entry_price = close_p
                entry_date = curr_date
                target_price = entry_price * (1 + take_profit_pct / 100)
                stop_price = entry_price * (1 - stop_loss_pct / 100)
                hold_count = 0
                shares = int(capital / entry_price) if entry_price > 0 else 0
                
        # Record equity
        current_portfolio_value = capital
        if in_trade:
            current_portfolio_value += (close_p - entry_price) * shares
            
        equity_curve.append({
            "date": curr_date,
            "equity": round(current_portfolio_value, 2)
        })
        
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t["win"])
    losing_trades = total_trades - winning_trades
    win_rate = round((winning_trades / total_trades * 100), 1) if total_trades > 0 else 0
    total_return_pct = round(((capital - initial_capital) / initial_capital) * 100, 2)
    
    # Calculate Max Drawdown
    equity_vals = [e["equity"] for e in equity_curve]
    if equity_vals:
        peak = equity_vals[0]
        max_dd = 0.0
        for val in equity_vals:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_dd:
                max_dd = dd
        max_drawdown_pct = round(max_dd, 2)
    else:
        max_drawdown_pct = 0.0
        
    return {
        "initialCapital": initial_capital,
        "finalCapital": round(capital, 2),
        "totalReturnPct": total_return_pct,
        "totalTrades": total_trades,
        "winningTrades": winning_trades,
        "losingTrades": losing_trades,
        "winRatePct": win_rate,
        "maxDrawdownPct": max_drawdown_pct,
        "equityCurve": equity_curve,
        "tradeLog": trades[-10:] # Return last 10 trades for display
    }
