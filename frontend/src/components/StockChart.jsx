import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer, ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Area
} from 'recharts';
import { Activity, RefreshCw, Zap, Clock } from 'lucide-react';

export default function StockChart({ stockData, selectedPeriod, selectedInterval, onTimeframeChange }) {
  const [chartType, setChartType] = useState('price_vol');
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    let intervalId;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        onTimeframeChange(selectedPeriod, selectedInterval);
      }, 10000); // 10s live polling
    }
    return () => clearInterval(intervalId);
  }, [autoRefresh, selectedPeriod, selectedInterval]);

  if (!stockData || !stockData.candles) return null;
  const { candles, symbol, latest } = stockData;

  const timeframes = [
    { label: '⚡ 1D Intraday (5m)', period: '1d', interval: '5m' },
    { label: '1M', period: '1mo', interval: '1d' },
    { label: '6M', period: '6mo', interval: '1d' },
    { label: '1Y', period: '1y', interval: '1d' },
    { label: '5Y', period: '5y', interval: '1d' }
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          background: 'rgba(12, 16, 26, 0.95)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '12px 16px',
          fontSize: '0.82rem',
          boxShadow: '0 10px 20px rgba(0,0,0,0.6)',
          fontFamily: 'var(--font-mono)'
        }}>
          <div style={{ color: 'var(--accent-gold)', fontWeight: 700, marginBottom: '6px' }}>{data.Date}</div>
          <div>Close: <strong style={{ color: '#FFF' }}>₹{data.Close}</strong></div>
          <div>VWAP: <strong style={{ color: 'var(--accent-blue)' }}>₹{data.VWAP}</strong></div>
          <div>Volume: <strong style={{ color: 'var(--accent-green)' }}>{data.Volume?.toLocaleString()}</strong></div>
          <div>Vol Surge: <strong>{data.Vol_Surge_Ratio}x</strong></div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
        <div className="card-title">
          <Activity color="var(--accent-green)" size={20} />
          {symbol} - Price Action & Volume Indicators
          {selectedInterval === '5m' && (
            <span className="badge badge-success" style={{ marginLeft: 6, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
              <span className="live-pulse"></span> INTRADAY LIVE (5m)
            </span>
          )}
        </div>

        {/* Timeframe selector & Auto-Refresh Toggle */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className={`btn ${autoRefresh ? 'btn-primary' : ''}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
          >
            <Clock size={14} /> Auto-Stream (10s): {autoRefresh ? 'ON' : 'OFF'}
          </button>

          {timeframes.map((tf) => (
            <button
              key={tf.label}
              className={`btn ${selectedPeriod === tf.period && selectedInterval === tf.interval ? 'btn-primary' : ''}`}
              onClick={() => onTimeframeChange(tf.period, tf.interval)}
              style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {chartType === 'price_vol' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ height: 260, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={candles} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="Date" stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                <YAxis domain={['auto', 'auto']} stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="Close" stroke="#00F5A0" fill="rgba(0, 245, 160, 0.08)" strokeWidth={2} name="Close Price" />
                <Line type="monotone" dataKey="VWAP" stroke="#38BDF8" strokeWidth={2} dot={false} name="VWAP" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div style={{ height: 140, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={candles} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="Date" hide />
                <YAxis stroke="var(--text-dim)" tick={{ fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="Volume" fill="#00F5A0" radius={[2, 2, 0, 0]} name="Volume" />
                <Line type="monotone" dataKey="Vol_SMA20" stroke="#FFD700" strokeWidth={1.5} dot={false} name="20-SMA Volume" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div style={{ height: 380, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={candles} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="Date" stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
              <YAxis stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="OBV" stroke="#A855F7" strokeWidth={2} dot={false} name="OBV" />
              <Line type="monotone" dataKey="OBV_EMA20" stroke="#FFD700" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="OBV 20 EMA" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
