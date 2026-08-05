import React, { useState, useEffect } from 'react';
import { Play, TrendingUp, ShieldAlert, Award, DollarSign } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { runBacktest } from '../services/api';

export default function Backtesting({ selectedSymbol, initialStrategy }) {
  const [volMult, setVolMult] = useState(initialStrategy ? initialStrategy.volumeMultiplier : 2.0);
  const [holdDays, setHoldDays] = useState(initialStrategy ? initialStrategy.holdingDays : 5);
  const [stopLoss, setStopLoss] = useState(initialStrategy ? initialStrategy.stopLossPct : 2.0);
  const [takeProfit, setTakeProfit] = useState(initialStrategy ? initialStrategy.takeProfitPct : 6.0);
  const [capital, setCapital] = useState(100000);
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialStrategy) {
      setVolMult(initialStrategy.volumeMultiplier);
      setHoldDays(initialStrategy.holdingDays);
      setStopLoss(initialStrategy.stopLossPct);
      setTakeProfit(initialStrategy.takeProfitPct);
    }
  }, [initialStrategy]);

  const handleRunBacktest = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest({
        symbol: selectedSymbol,
        volumeMultiplier: parseFloat(volMult),
        holdingDays: parseInt(holdDays),
        stopLossPct: parseFloat(stopLoss),
        takeProfitPct: parseFloat(takeProfit),
        initialCapital: parseFloat(capital)
      });
      setResult(data);
    } catch (err) {
      setError("Failed to execute backtest for this ticker.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleRunBacktest();
  }, [selectedSymbol, volMult, holdDays, stopLoss, takeProfit]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Play color="var(--accent-green)" size={20} />
          Volume Strategy Backtester - {selectedSymbol}
          {initialStrategy && (
            <span className="badge badge-warning" style={{ fontSize: '0.75rem', marginLeft: 8 }}>
              Applied AI Zero-Loss Strategy
            </span>
          )}
        </div>
      </div>

      {/* Control Form Parameters */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '14px',
        background: 'var(--bg-subtle)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}>
        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
            Volume Surge Multiplier
          </label>
          <select
            value={volMult}
            onChange={(e) => setVolMult(e.target.value)}
            style={{ width: '100%', background: 'var(--bg-card)', color: '#FFF', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '6px' }}
          >
            <option value="1.5">1.5x Avg Volume</option>
            <option value="1.8">1.8x Avg Volume</option>
            <option value="2.0">2.0x Avg Volume</option>
            <option value="2.5">2.5x Avg Volume</option>
            <option value="3.0">3.0x Avg Volume</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
            Max Holding Period (Days)
          </label>
          <input
            type="number"
            value={holdDays}
            onChange={(e) => setHoldDays(e.target.value)}
            style={{ width: '100%', background: 'var(--bg-card)', color: '#FFF', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '6px' }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
            Stop Loss (%)
          </label>
          <input
            type="number"
            step="0.5"
            value={stopLoss}
            onChange={(e) => setStopLoss(e.target.value)}
            style={{ width: '100%', background: 'var(--bg-card)', color: '#FFF', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '6px' }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
            Target Profit (%)
          </label>
          <input
            type="number"
            step="0.5"
            value={takeProfit}
            onChange={(e) => setTakeProfit(e.target.value)}
            style={{ width: '100%', background: 'var(--bg-card)', color: '#FFF', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '6px' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={handleRunBacktest} disabled={loading}>
            {loading ? "Simulating..." : "Run Backtest"}
          </button>
        </div>
      </div>

      {/* Results View */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '10px' }}>
          <div className="metrics-row">
            <div className="metric-card">
              <div className="metric-title">Total Return</div>
              <div className={`metric-value ${result.totalReturnPct >= 0 ? 'text-green' : 'text-red'}`}>
                {result.totalReturnPct >= 0 ? `+${result.totalReturnPct}%` : `${result.totalReturnPct}%`}
              </div>
              <div className="metric-sub">Final Equity: ₹{result.finalCapital?.toLocaleString()}</div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Win Rate</div>
              <div className="metric-value text-green">{result.winRatePct}%</div>
              <div className="metric-sub">{result.winningTrades} Wins / {result.losingTrades} Losses</div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Max Drawdown</div>
              <div className="metric-value text-red">-{result.maxDrawdownPct}%</div>
              <div className="metric-sub">Peak to trough risk</div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Total Trades</div>
              <div className="metric-value">{result.totalTrades}</div>
              <div className="metric-sub">Executed signals</div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          {result.equityCurve && result.equityCurve.length > 0 && (
            <div style={{ height: 240, width: '100%' }}>
              <div style={{ fontSize: '0.88rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
                Portfolio Equity Growth Curve
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={result.equityCurve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" stroke="var(--text-dim)" tick={{ fontSize: 10 }} />
                  <YAxis domain={['auto', 'auto']} stroke="var(--text-dim)" tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Portfolio Value']} />
                  <Area type="monotone" dataKey="equity" stroke="#00F5A0" fill="rgba(0, 245, 160, 0.15)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Trades Log Table */}
          {result.tradeLog && result.tradeLog.length > 0 && (
            <div>
              <div style={{ fontSize: '0.88rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
                Recent Backtested Trade Log
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Entry Date</th>
                      <th>Exit Date</th>
                      <th>Entry Price</th>
                      <th>Exit Price</th>
                      <th>P&L %</th>
                      <th>Exit Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.tradeLog.map((t, idx) => (
                      <tr key={idx}>
                        <td>{t.entryDate}</td>
                        <td>{t.exitDate}</td>
                        <td>₹{t.entryPrice}</td>
                        <td>₹{t.exitPrice}</td>
                        <td className={t.pnlPct >= 0 ? 'text-green' : 'text-red'}>
                          {t.pnlPct >= 0 ? `+${t.pnlPct}%` : `${t.pnlPct}%`}
                        </td>
                        <td>
                          <span className={t.win ? "badge badge-success" : "badge badge-danger"}>
                            {t.reason}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
