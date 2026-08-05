import React, { useState, useEffect } from 'react';
import { DollarSign, ShieldAlert, Award, TrendingUp, ArrowUpRight, ArrowDownRight, RefreshCw, X, Play, ShieldCheck } from 'lucide-react';
import { fetchPaperPortfolio, executePaperBuy, closePaperPosition, resetPaperAccount } from '../services/api';

export default function PaperTrading({ selectedSymbol }) {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [msg, setMsg] = useState(null);

  const loadPortfolio = async () => {
    setLoading(true);
    try {
      const data = await fetchPaperPortfolio();
      setPortfolio(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolio();
  }, [selectedSymbol]);

  const handleExecutePaperBuy = async () => {
    setExecuting(true);
    setMsg(null);
    try {
      const res = await executePaperBuy(selectedSymbol, 2.0, 6.0);
      setMsg({ type: 'success', text: res.message });
      await loadPortfolio();
    } catch (err) {
      setMsg({ type: 'error', text: err.message || "Failed to execute paper buy order." });
    } finally {
      setExecuting(false);
    }
  };

  const handleClosePos = async (posId) => {
    try {
      const res = await closePaperPosition(posId);
      setMsg({ type: 'success', text: res.message });
      await loadPortfolio();
    } catch (err) {
      setMsg({ type: 'error', text: "Failed to close position." });
    }
  };

  const handleResetAccount = async () => {
    if (window.confirm("Are you sure you want to reset your virtual paper account to ₹100,000?")) {
      await resetPaperAccount();
      await loadPortfolio();
    }
  };

  if (!portfolio) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Portfolio Header Cards */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #121826 0%, #172033 100%)', border: '1px solid var(--border-active)' }}>
        <div className="card-header">
          <div className="card-title">
            <DollarSign color="var(--accent-green)" size={24} />
            Virtual Paper Trading Simulator & Risk Engine Portfolio
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-primary" onClick={handleExecutePaperBuy} disabled={executing}>
              <Play size={16} /> Execute Paper Buy ({selectedSymbol})
            </button>
            <button className="btn" onClick={handleResetAccount}>
              <RefreshCw size={14} /> Reset Virtual Account
            </button>
          </div>
        </div>

        {msg && (
          <div style={{
            padding: '12px 16px',
            borderRadius: '8px',
            background: msg.type === 'success' ? 'rgba(0, 245, 160, 0.12)' : 'rgba(255, 51, 102, 0.12)',
            border: `1px solid ${msg.type === 'success' ? 'var(--accent-green)' : 'var(--accent-red)'}`,
            color: msg.type === 'success' ? 'var(--accent-green)' : 'var(--accent-red)',
            fontSize: '0.88rem',
            marginTop: '8px'
          }}>
            {msg.text}
          </div>
        )}

        <div className="metrics-row" style={{ marginTop: '12px' }}>
          <div className="metric-card">
            <div className="metric-title">Virtual Cash Balance</div>
            <div className="metric-value">₹{portfolio.cashBalance?.toLocaleString()}</div>
            <div className="metric-sub" style={{ color: 'var(--text-muted)' }}>Initial: ₹{portfolio.initialCapital?.toLocaleString()}</div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Total Portfolio Value</div>
            <div className="metric-value" style={{ color: portfolio.totalPnl >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              ₹{portfolio.totalPortfolioValue?.toLocaleString()}
            </div>
            <div className={`metric-sub ${portfolio.totalPnl >= 0 ? 'text-green' : 'text-red'}`}>
              {portfolio.totalPnl >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              {portfolio.totalPnl >= 0 ? `+₹${portfolio.totalPnl} (+${portfolio.totalPnlPct}%)` : `-₹${Math.abs(portfolio.totalPnl)} (${portfolio.totalPnlPct}%)`}
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Risk Engine Sizing Rule</div>
            <div className="metric-value text-gold">2.0%</div>
            <div className="metric-sub text-green">
              <ShieldCheck size={14} /> Max risk per trade auto-capped
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Win Rate</div>
            <div className="metric-value text-green">{portfolio.winRatePct}%</div>
            <div className="metric-sub">{portfolio.closedTradesCount} Trades Executed</div>
          </div>
        </div>
      </div>

      {/* Open Positions Section */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <TrendingUp color="var(--accent-green)" size={20} />
            Active Open Paper Positions ({portfolio.openPositionsCount})
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>Shares</th>
                <th>Investment</th>
                <th>Stop Loss</th>
                <th>Target</th>
                <th>Unrealized PnL</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.openPositions && portfolio.openPositions.length > 0 ? (
                portfolio.openPositions.map((pos) => (
                  <tr key={pos.id}>
                    <td><strong style={{ color: '#FFF' }}>{pos.symbol}</strong></td>
                    <td>₹{pos.entryPrice}</td>
                    <td>₹{pos.currentPrice}</td>
                    <td>{pos.shares}</td>
                    <td>₹{pos.totalInvestment?.toLocaleString()}</td>
                    <td className="text-red">₹{pos.stopLossPrice}</td>
                    <td className="text-green">₹{pos.targetPrice}</td>
                    <td className={pos.unrealizedPnl >= 0 ? 'text-green' : 'text-red'} style={{ fontWeight: 700 }}>
                      {pos.unrealizedPnl >= 0 ? `+₹${pos.unrealizedPnl}` : `-₹${Math.abs(pos.unrealizedPnl)}`} ({pos.pnlPct}%)
                    </td>
                    <td>
                      <button
                        className="btn"
                        style={{ padding: '4px 10px', fontSize: '0.78rem', background: 'rgba(255,51,102,0.15)', color: 'var(--accent-red)', border: '1px solid var(--accent-red)' }}
                        onClick={() => handleClosePos(pos.id)}
                      >
                        <X size={12} /> Close Trade
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                    No active open paper positions. Click <strong>"Execute Paper Buy"</strong> to open a virtual trade.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Closed Trades History Table */}
      {portfolio.tradeHistory && portfolio.tradeHistory.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Award color="var(--accent-gold)" size={20} />
              Closed Trade Audit History Log
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Entry Price</th>
                  <th>Exit Price</th>
                  <th>Shares</th>
                  <th>Realized PnL</th>
                  <th>PnL %</th>
                  <th>Exit Reason</th>
                  <th>Entry Time</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.tradeHistory.map((t) => (
                  <tr key={t.id}>
                    <td><strong style={{ color: '#FFF' }}>{t.symbol}</strong></td>
                    <td>₹{t.entryPrice}</td>
                    <td>₹{t.exitPrice}</td>
                    <td>{t.shares}</td>
                    <td className={t.pnl >= 0 ? 'text-green' : 'text-red'} style={{ fontWeight: 700 }}>
                      {t.pnl >= 0 ? `+₹${t.pnl}` : `-₹${Math.abs(t.pnl)}`}
                    </td>
                    <td className={t.pnlPct >= 0 ? 'text-green' : 'text-red'}>{t.pnlPct}%</td>
                    <td>
                      <span className={t.pnl >= 0 ? "badge badge-success" : "badge badge-danger"}>
                        {t.exitReason}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{t.entryTime}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
