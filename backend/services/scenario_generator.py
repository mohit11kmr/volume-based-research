import pandas as pd
import numpy as np
from typing import Dict, Any, List
from services.backtester import run_volume_backtest

def generate_candidate_scenarios() -> List[Dict[str, Any]]:
    """Generate candidate strategy scenarios with varied parameters."""
    scenarios = []
    
    vol_mults = [1.5, 1.8, 2.0, 2.5, 3.0]
    hold_days_list = [3, 5, 7, 10]
    stop_losses = [1.0, 1.5, 2.0, 3.0]
    take_profits = [3.0, 5.0, 7.0, 10.0, 12.0]
    
    scenario_id = 1
    for v_mult in vol_mults:
        for hold_d in hold_days_list:
            for sl in stop_losses:
                for tp in take_profits:
                    # Filter out bad risk-reward ratios
                    if tp <= sl:
                        continue
                    scenarios.append({
                        "id": f"SCN-{scenario_id:03d}",
                        "name": f"VolSurge {v_mult}x | SL {sl}% | TP {tp}%",
                        "volumeMultiplier": float(v_mult),
                        "holdingDays": int(hold_d),
                        "stopLossPct": float(sl),
                        "takeProfitPct": float(tp)
                    })
                    scenario_id += 1
                    if scenario_id > 60:
                        break
                if scenario_id > 60:
                    break
            if scenario_id > 60:
                break
        if scenario_id > 60:
            break
            
    return scenarios

def evaluate_and_rank_scenarios(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Execute backtests across all candidate scenarios and rank by Zero-Loss & Win Rate."""
    if df.empty or len(df) < 25:
        return {"error": "Insufficient data for scenario generation."}
        
    candidates = generate_candidate_scenarios()
    evaluated = []
    
    for scn in candidates:
        res = run_volume_backtest(
            df=df,
            volume_multiplier=scn["volumeMultiplier"],
            holding_days=scn["holdingDays"],
            stop_loss_pct=scn["stopLossPct"],
            take_profit_pct=scn["takeProfitPct"],
            initial_capital=100000.0
        )
        
        total_trades = res.get("totalTrades", 0)
        win_rate = res.get("winRatePct", 0.0)
        total_return = res.get("totalReturnPct", 0.0)
        max_dd = res.get("maxDrawdownPct", 0.0)
        losing_trades = res.get("losingTrades", 0)
        winning_trades = res.get("winningTrades", 0)
        
        is_zero_loss = (losing_trades == 0 and total_trades >= 2)
        is_low_risk = (max_dd <= 2.5 and win_rate >= 80.0 and total_trades >= 3)
        
        # Calculate Scenario Score
        score = (win_rate * 2.0) + (total_return * 1.5) - (max_dd * 3.0)
        if is_zero_loss:
            score += 150.0
        elif is_low_risk:
            score += 75.0
            
        evaluated.append({
            "scenarioId": scn["id"],
            "name": scn["name"],
            "volumeMultiplier": scn["volumeMultiplier"],
            "holdingDays": scn["holdingDays"],
            "stopLossPct": scn["stopLossPct"],
            "takeProfitPct": scn["takeProfitPct"],
            "totalTrades": total_trades,
            "winningTrades": winning_trades,
            "losingTrades": losing_trades,
            "winRatePct": win_rate,
            "totalReturnPct": total_return,
            "maxDrawdownPct": max_dd,
            "isZeroLoss": is_zero_loss,
            "isLowRisk": is_low_risk,
            "score": round(score, 2)
        })
        
    # Sort scenarios by score descending
    evaluated.sort(key=lambda x: x["score"], reverse=True)
    
    zero_loss_setups = [e for e in evaluated if e["isZeroLoss"]]
    top_scenarios = evaluated[:8]
    
    return {
        "symbol": symbol,
        "totalScenariosEvaluated": len(evaluated),
        "zeroLossScenariosFound": len(zero_loss_setups),
        "topScenarios": top_scenarios,
        "zeroLossScenarios": zero_loss_setups[:5] if zero_loss_setups else top_scenarios[:3]
    }
