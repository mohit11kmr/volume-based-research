import React from 'react';
import { Activity, ArrowUpRight, ArrowDownRight, Zap, ShieldAlert, BarChart3 } from 'lucide-react';

export default function MarketSummary({ stockData, popularStocks, onSelectSymbol }) {
  if (!stockData) return null;
  const { symbol, latest } = stockData;
  
  const closeP = latest.Close || 0;
  const pChange = latest.Price_Change_Pct || 0;
  const surgeRatio = latest.Vol_Surge_Ratio || 1.0;
  const cmf = latest.CMF || 0;
  const vol = latest.Volume ? (latest.Volume / 100000).toFixed(2) + " L" : "N/A";
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Ticker Bar */}
      <div className="ticker-bar">
        <span style={{ color: 'var(--accent-gold)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Zap size={14} /> LIVE TICKER:
        </span>
        {popularStocks.slice(0, 8).map(stk => (
          <div key={stk.symbol} className="ticker-item" onClick={() => onSelectSymbol(stk.symbol)}>
            <span className="ticker-symbol">{stk.symbol}</span>
            <span className="ticker-surge surge-high">HOT</span>
          </div>
        ))}
      </div>

      {/* Stock Key Metrics Cards */}
      <div className="metrics-row">
        <div className="metric-card">
          <div className="metric-title">{symbol} Price</div>
          <div className="metric-value">₹ {closeP.toLocaleString()}</div>
          <div className={`metric-sub ${pChange >= 0 ? 'text-green' : 'text-red'}`}>
            {pChange >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            {pChange >= 0 ? `+${pChange}%` : `${pChange}%`} Today
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Volume Surge Multiple</div>
          <div className="metric-value" style={{ color: surgeRatio >= 1.8 ? 'var(--accent-green)' : 'var(--text-main)' }}>
            {surgeRatio}x
          </div>
          <div className="metric-sub text-green">
            <Activity size={14} /> vs 20-Day SMA Volume
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Chaikin Money Flow (CMF)</div>
          <div className="metric-value" style={{ color: cmf > 0.1 ? 'var(--accent-green)' : cmf < -0.1 ? 'var(--accent-red)' : 'var(--accent-gold)' }}>
            {cmf}
          </div>
          <div className="metric-sub" style={{ color: 'var(--text-muted)' }}>
            {cmf > 0.1 ? '💚 Strong Institutional Inflow' : cmf < -0.1 ? '🔴 Selling Outflow' : '⚖️ Neutral Flow'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Volume Traded</div>
          <div className="metric-value">{vol}</div>
          <div className="metric-sub text-gold">
            <BarChart3 size={14} /> Shares traded today
          </div>
        </div>
      </div>
    </div>
  );
}
