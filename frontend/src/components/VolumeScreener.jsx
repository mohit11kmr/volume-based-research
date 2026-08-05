import React, { useState, useEffect } from 'react';
import { Filter, Zap, ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react';
import { fetchVolumeScreener } from '../services/api';

export default function VolumeScreener({ onSelectSymbol }) {
  const [minSurge, setMinSurge] = useState(1.5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadScreenerData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchVolumeScreener(minSurge);
      setResults(data.screenerResults || []);
    } catch (err) {
      setError("Unable to connect to screener backend service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScreenerData();
  }, [minSurge]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Zap color="var(--accent-green)" size={20} />
          Volume Surge Screener & Institutional Accumulation Scanner
        </div>
        <button className="btn" onClick={loadScreenerData} disabled={loading}>
          <RefreshCw size={14} className={loading ? "spin" : ""} /> Refresh Scan
        </button>
      </div>

      {/* Filters Bar */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Filter size={16} /> Volume Multiple Threshold:
        </span>
        {[1.2, 1.5, 2.0, 3.0, 5.0].map((threshold) => (
          <button
            key={threshold}
            className={`btn ${minSurge === threshold ? 'btn-primary' : ''}`}
            onClick={() => setMinSurge(threshold)}
            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
          >
            &ge; {threshold}x SMA20
          </button>
        ))}
      </div>

      {/* Screener Table */}
      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Scanning NSE & Global markets for volume surges...
        </div>
      ) : error ? (
        <div style={{ padding: '20px', color: 'var(--accent-red)' }}>{error}</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Stock</th>
                <th>Sector / Exchange</th>
                <th>Price</th>
                <th>Price Change</th>
                <th>Vol Surge Multiple</th>
                <th>CMF Flow</th>
                <th>Institutional Signal</th>
              </tr>
            </thead>
            <tbody>
              {results.length > 0 ? (
                results.map((stk) => (
                  <tr key={stk.symbol} onClick={() => onSelectSymbol(stk.symbol)}>
                    <td>
                      <strong style={{ color: '#FFF' }}>{stk.symbol}</strong>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stk.name}</span>
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>{stk.sector} ({stk.exchange})</td>
                    <td>₹{stk.closePrice?.toLocaleString()}</td>
                    <td className={stk.priceChangePct >= 0 ? 'text-green' : 'text-red'}>
                      {stk.priceChangePct >= 0 ? `+${stk.priceChangePct}%` : `${stk.priceChangePct}%`}
                    </td>
                    <td>
                      <span className="badge badge-success" style={{ fontFamily: 'var(--font-mono)' }}>
                        🔥 {stk.volumeSurgeRatio}x
                      </span>
                    </td>
                    <td style={{ color: stk.cmf > 0.1 ? 'var(--accent-green)' : 'var(--text-muted)' }}>
                      {stk.cmf}
                    </td>
                    <td>
                      <span className={
                        stk.signal.includes("Bullish") ? "badge badge-success" :
                        stk.signal.includes("Bearish") ? "badge badge-danger" : "badge badge-warning"
                      }>
                        {stk.signal}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                    No stocks currently trading above {minSurge}x average volume. Try lowering the threshold.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
