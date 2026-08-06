import math
import os
import json
import threading
import hashlib
from typing import Dict, Any, List
from datetime import datetime

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def _sanitize_user_id(user_id: str) -> str:
    """Hash arbitrary user ids to a safe filename fragment."""
    if not user_id:
        return "default"
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]
    return f"user_{digest}"

def _state_path_for(user_id: str) -> str:
    return os.path.join(STATE_DIR, f"paper_{_sanitize_user_id(user_id)}.json")

class RiskEngine:
    def __init__(self, max_risk_per_trade_pct: float = 2.0, max_daily_drawdown_pct: float = 3.0):
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_daily_drawdown_pct = max_daily_drawdown_pct

    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss_pct: float
    ) -> Dict[str, Any]:
        """Calculate optimal position size ensuring max risk per trade does not exceed risk limit."""
        if entry_price <= 0 or capital <= 0 or stop_loss_pct <= 0:
            return {"shares": 0, "totalInvestment": 0.0, "maxLossRiskAmount": 0.0}

        # Maximum cash risk allowed for this single trade
        max_risk_amount = capital * (self.max_risk_per_trade_pct / 100.0)
        
        # Risk per share in currency
        risk_per_share = entry_price * (stop_loss_pct / 100.0)
        
        if risk_per_share <= 0:
            shares = int(capital / entry_price)
        else:
            # Position size = Max Risk Amount / Risk Per Share
            shares = math.floor(max_risk_amount / risk_per_share)
            
        total_investment = shares * entry_price
        
        # Cap investment to available capital
        if total_investment > capital:
            shares = math.floor(capital / entry_price)
            total_investment = shares * entry_price
            
        actual_risk_amount = round(shares * risk_per_share, 2)
        
        return {
            "shares": shares,
            "entryPrice": round(entry_price, 2),
            "totalInvestment": round(total_investment, 2),
            "maxLossRiskAmount": actual_risk_amount,
            "capitalRiskPct": round((actual_risk_amount / capital) * 100.0, 2)
        }

    def validate_trade_risk(
        self,
        capital: float,
        daily_pnl: float,
        proposed_investment: float
    ) -> Dict[str, Any]:
        """Validate whether proposed trade violates daily drawdown limits or capital constraints."""
        max_allowed_daily_loss = capital * (self.max_daily_drawdown_pct / 100.0)
        
        if daily_pnl <= -max_allowed_daily_loss:
            return {
                "approved": False,
                "reason": f"DAILY KILL SWITCH TRIGGERED: Daily loss (-₹{abs(daily_pnl):,.2f}) exceeded max drawdown limit ({self.max_daily_drawdown_pct}%)."
            }
            
        if proposed_investment > capital:
            return {
                "approved": False,
                "reason": f"INSUFFICIENT CAPITAL: Proposed investment (₹{proposed_investment:,.2f}) exceeds available capital (₹{capital:,.2f})."
            }
            
        return {"approved": True, "reason": "Trade risk validated successfully."}


class PaperTradingSimulator:
    def __init__(self, initial_capital: float = 100000.0, user_id: str = "default"):
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        self.open_positions: List[Dict[str, Any]] = []
        self.closed_trades: List[Dict[str, Any]] = []
        self.next_position_id = 1
        self.risk_engine = RiskEngine(max_risk_per_trade_pct=2.0, max_daily_drawdown_pct=3.0)
        self.state_path = _state_path_for(user_id)
        self._load_state()

    def _save_state(self):
        """Persist portfolio state to disk so it survives server restarts."""
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            state = {
                "initialCapital": self.initial_capital,
                "cashBalance": self.cash_balance,
                "openPositions": self.open_positions,
                "closedTrades": self.closed_trades,
                "nextPositionId": self.next_position_id
            }
            with open(self.state_path, "w") as f:
                json.dump(state, f, indent=2, default=str)
        except Exception:
            pass

    def _load_state(self):
        """Restore previously persisted portfolio state if available."""
        if not os.path.exists(self.state_path):
            return
        try:
            with open(self.state_path) as f:
                state = json.load(f)
            self.initial_capital = float(state.get("initialCapital", self.initial_capital))
            self.cash_balance = float(state.get("cashBalance", self.initial_capital))
            self.open_positions = state.get("openPositions", [])
            self.closed_trades = state.get("closedTrades", [])
            self.next_position_id = int(state.get("nextPositionId", 1))
        except Exception:
            pass

    def get_portfolio_summary(self, live_prices: Dict[str, float] = None) -> Dict[str, Any]:
        """Return virtual portfolio balance, open positions, and total PnL metrics."""
        live_prices = live_prices or {}
        unrealized_pnl = 0.0
        
        # Calculate live unrealized PnL for open positions
        for pos in self.open_positions:
            sym = pos["symbol"]
            curr_price = live_prices.get(sym, pos["entryPrice"])
            pos["currentPrice"] = round(curr_price, 2)
            pos_pnl = (curr_price - pos["entryPrice"]) * pos["shares"]
            pos["unrealizedPnl"] = round(pos_pnl, 2)
            pos["pnlPct"] = round(((curr_price - pos["entryPrice"]) / pos["entryPrice"]) * 100.0, 2)
            unrealized_pnl += pos_pnl

        realized_pnl = sum(t["pnl"] for t in self.closed_trades)
        total_portfolio_value = self.cash_balance + sum(p["totalInvestment"] for p in self.open_positions) + unrealized_pnl
        total_pnl = round(total_portfolio_value - self.initial_capital, 2)
        total_pnl_pct = round((total_pnl / self.initial_capital) * 100.0, 2)

        total_closed = len(self.closed_trades)
        wins = sum(1 for t in self.closed_trades if t["pnl"] > 0)
        win_rate = round((wins / total_closed * 100.0), 1) if total_closed > 0 else 0.0

        return {
            "initialCapital": self.initial_capital,
            "cashBalance": round(self.cash_balance, 2),
            "totalPortfolioValue": round(total_portfolio_value, 2),
            "realizedPnl": round(realized_pnl, 2),
            "unrealizedPnl": round(unrealized_pnl, 2),
            "totalPnl": total_pnl,
            "totalPnlPct": total_pnl_pct,
            "winRatePct": win_rate,
            "openPositionsCount": len(self.open_positions),
            "closedTradesCount": total_closed,
            "openPositions": self.open_positions,
            "tradeHistory": self.closed_trades[-15:] # Last 15 closed trades
        }

    def execute_paper_buy(
        self,
        symbol: str,
        current_price: float,
        stop_loss_pct: float = 2.0,
        take_profit_pct: float = 6.0
    ) -> Dict[str, Any]:
        """Execute a virtual paper trade using Risk Engine position sizing."""
        # Calculate position sizing using 2% Risk Engine Rule
        size_info = self.risk_engine.calculate_position_size(self.cash_balance, current_price, stop_loss_pct)
        shares = size_info["shares"]
        investment = size_info["totalInvestment"]

        if shares <= 0:
            return {"success": False, "message": "Insufficient cash balance or position size too small."}

        # Check risk limits
        daily_pnl = sum(t["pnl"] for t in self.closed_trades)
        risk_check = self.risk_engine.validate_trade_risk(self.cash_balance, daily_pnl, investment)
        if not risk_check["approved"]:
            return {"success": False, "message": risk_check["reason"]}

        # Deduct cash & create position
        self.cash_balance -= investment
        stop_price = round(current_price * (1.0 - stop_loss_pct / 100.0), 2)
        target_price = round(current_price * (1.0 + take_profit_pct / 100.0), 2)

        pos = {
            "id": self.next_position_id,
            "symbol": symbol.upper(),
            "entryPrice": round(current_price, 2),
            "currentPrice": round(current_price, 2),
            "shares": shares,
            "totalInvestment": round(investment, 2),
            "stopLossPrice": stop_price,
            "targetPrice": target_price,
            "unrealizedPnl": 0.0,
            "pnlPct": 0.0,
            "entryTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.open_positions.append(pos)
        self.next_position_id += 1
        self._save_state()

        return {
            "success": True,
            "message": f"Successfully executed Paper Buy for {shares} shares of {symbol} at ₹{current_price} (Risk: ₹{size_info['maxLossRiskAmount']}).",
            "position": pos
        }

    def close_position(self, position_id: int, exit_price: float, reason: str = "Manual Exit") -> Dict[str, Any]:
        """Close an active paper position and credit portfolio cash."""
        pos = next((p for p in self.open_positions if p["id"] == position_id), None)
        if not pos:
            return {"success": False, "message": "Position ID not found."}

        self.open_positions.remove(pos)
        exit_p = round(exit_price, 2)
        pnl = round((exit_p - pos["entryPrice"]) * pos["shares"], 2)
        pnl_pct = round(((exit_p - pos["entryPrice"]) / pos["entryPrice"]) * 100.0, 2)

        # Credit return to cash
        returned_cash = pos["totalInvestment"] + pnl
        self.cash_balance += returned_cash

        trade_log = {
            "id": pos["id"],
            "symbol": pos["symbol"],
            "entryPrice": pos["entryPrice"],
            "exitPrice": exit_p,
            "shares": pos["shares"],
            "totalInvestment": pos["totalInvestment"],
            "pnl": pnl,
            "pnlPct": pnl_pct,
            "exitReason": reason,
            "entryTime": pos["entryTime"],
            "exitTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.closed_trades.append(trade_log)
        self._save_state()

        return {
            "success": True,
            "message": f"Closed position {pos['symbol']} at ₹{exit_p} (PnL: {'+₹' if pnl>=0 else '-₹'}{abs(pnl)} / {pnl_pct}%).",
            "trade": trade_log
        }

    def reset_portfolio(self):
        """Reset virtual paper account to initial capital."""
        self.cash_balance = self.initial_capital
        self.open_positions = []
        self.closed_trades = []
        self.next_position_id = 1
        self._save_state()


class PaperTradingManager:
    """Thread-safe registry of per-user PaperTradingSimulator instances.

    Every user id gets its own isolated portfolio persisted to a separate
    JSON state file. Unknown/blank ids share the "default" portfolio.
    """

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self._sims: Dict[str, PaperTradingSimulator] = {}
        self._lock = threading.Lock()

    def get(self, user_id: str) -> PaperTradingSimulator:
        uid = _sanitize_user_id(user_id or "default")
        with self._lock:
            if uid not in self._sims:
                self._sims[uid] = PaperTradingSimulator(
                    initial_capital=self.initial_capital,
                    user_id=uid
                )
            return self._sims[uid]

    def reset_all(self):
        with self._lock:
            for sim in self._sims.values():
                sim.reset_portfolio()
