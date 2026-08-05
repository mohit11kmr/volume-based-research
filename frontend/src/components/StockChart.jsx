import React, { useState } from 'react';
import {
  ResponsiveContainer, ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Area
} from 'recharts';
import { Layers, Activity, TrendingUp } from 'lucide-react';

export default function StockChart({ stockData }) {
  const [chartType, setChartType] = useState('price_vol'); // 'price_vol' or 'obv'
  
  if (!stockData || !stockData.candles) return null;
  const { candles, symbol } = stockData;

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
          <div>OBV: <span>{data.OBV?.toLocaleString()}</span></div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Activity color="var(--accent-green)" size={20} />
          {symbol} - Price Action & Volume Technical Indicators
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${chartType === 'price_vol' ? 'btn-primary' : ''}`}
            onClick={() => setChartType('price_vol')}
          >
            Price + VWAP + Volume
          </button>
          <button
            className={`btn ${chartType === 'obv' ? 'btn-primary' : ''}`}
            onClick={() => setChartType('obv')}
          >
            OBV & Money Flow
          </button>
        </div>
      </div>

      {chartType === 'price_vol' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Price & VWAP Chart */}
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

          {/* Volume Bars & 20 SMA Volume Line */}
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
        /* OBV Panel */
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
