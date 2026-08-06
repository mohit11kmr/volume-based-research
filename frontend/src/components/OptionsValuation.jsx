import React, { useState, useEffect } from 'react';
import { Layers, ShieldCheck, Tag, TrendingUp, RefreshCw, Zap } from 'lucide-react';
import { fetchOptionsValuation } from '../services/api';

export default function OptionsValuation({ selectedSymbol }) {
  const [data, setData] = useState(null);
  const [daysToExpiry, setDaysToExpiry] = useState(7);
  const [loading, setLoading] = useState(true);

  const loadOptionsData = async () => {
    setLoading(true);
    try {
      const res = await fetchOptionsValuation(selectedSymbol, daysToExpiry);
      setData(res);
    } catch (err) {
      console.error("Failed to load options data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOptionsData();
  }, [selectedSymbol, daysToExpiry]);

  if (!data) return null;

  const { underlyingPrice, impliedVolatilityPct, atmStrike, optionChain, recommendation } = data;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ background: 'linear-gradient(135deg, #121826 0%, #172033 100%)', border: '1px solid var(--border-active)' }}>
        <div className="card-header">
          <div className="card-title">
            <Tag color="var(--accent-gold)" size={24} />
            Option Premium Valuation & Greeks Engine - {data.symbol}
            <span
              className={data.isRealData ? "badge badge-success" : "badge badge-warning"}
              style={{ marginLeft: 8, fontSize: '0.72rem' }}
            >
              {data.isRealData ? "LIVE CHAIN" : "BS ESTIMATE"}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Expiry:</span>
            {[3, 7, 14, 30].map((d) => (
              <button
                key={d}
                className={`btn ${daysToExpiry === d ? 'btn-primary' : ''}`}
                onClick={() => setDaysToExpiry(d)}
                style={{ padding: '4px 10px', fontSize: '0.78rem' }}
              >
                {d} Days
              </button>
            ))}
          </div>
        </div>

        {/* Spot Price & IV Summary */}
        <div className="metrics-row" style={{ marginTop: '12px' }}>
          <div className="metric-card">
            <div className="metric-title">Underlying Spot Price</div>
            <div className="metric-value">₹{underlyingPrice}</div>
            <div className="metric-sub text-green">ATM Strike: ₹{atmStrike}</div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Implied Volatility (IV)</div>
            <div className="metric-value text-gold">{impliedVolatilityPct}%</div>
            <div className="metric-sub">Black-Scholes Model</div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Best Call Strike Rating</div>
            <div className="metric-value text-green">₹{recommendation?.bestCallStrike} CE</div>
            <div className="metric-sub text-green">{recommendation?.bestCallValuation}</div>
          </div>

          <div className="metric-card">
            <div className="metric-title">Best Put Strike Rating</div>
            <div className="metric-value text-gold">₹{recommendation?.bestPutStrike} PE</div>
            <div className="metric-sub text-gold">{recommendation?.bestPutValuation}</div>
          </div>
        </div>
      </div>

      {/* Option Chain Valuation Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Layers color="var(--accent-blue)" size={20} />
            Option Chain Fair Value vs Market Premium Matrix
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th colSpan="4" style={{ textAlign: 'center', background: 'rgba(0, 245, 160, 0.1)', color: 'var(--accent-green)' }}>CALL OPTIONS (CE)</th>
                <th style={{ textAlign: 'center', background: 'var(--bg-card)' }}>STRIKE</th>
                <th colSpan="4" style={{ textAlign: 'center', background: 'rgba(255, 51, 102, 0.1)', color: 'var(--accent-red)' }}>PUT OPTIONS (PE)</th>
              </tr>
              <tr>
                <th>Market Price</th>
                <th>Fair Value</th>
                <th>Valuation</th>
                <th>Delta</th>
                <th style={{ textAlign: 'center' }}>Price</th>
                <th>Market Price</th>
                <th>Fair Value</th>
                <th>Valuation</th>
                <th>Delta</th>
              </tr>
            </thead>
            <tbody>
              {optionChain && optionChain.map((opt) => (
                <tr key={opt.strikePrice} style={{ background: opt.isATM ? 'rgba(255, 215, 0, 0.08)' : 'transparent' }}>
                  <td>₹{opt.call.marketPremium}</td>
                  <td style={{ color: 'var(--text-muted)' }}>₹{opt.call.fairValue}</td>
                  <td>
                    <span className={
                      opt.call.valuation.includes("CHEAP") ? "badge badge-success" :
                      opt.call.valuation.includes("EXPENSIVE") ? "badge badge-danger" : "badge badge-warning"
                    }>
                      {opt.call.valuation}
                    </span>
                  </td>
                  <td>{opt.call.delta}</td>

                  <td style={{ textAlign: 'center', fontWeight: 700, color: opt.isATM ? 'var(--accent-gold)' : '#FFF' }}>
                    {opt.strikePrice} {opt.isATM && '(ATM)'}
                  </td>

                  <td>₹{opt.put.marketPremium}</td>
                  <td style={{ color: 'var(--text-muted)' }}>₹{opt.put.fairValue}</td>
                  <td>
                    <span className={
                      opt.put.valuation.includes("CHEAP") ? "badge badge-success" :
                      opt.put.valuation.includes("EXPENSIVE") ? "badge badge-danger" : "badge badge-warning"
                    }>
                      {opt.put.valuation}
                    </span>
                  </td>
                  <td>{opt.put.delta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
