import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function AIInsights({ stockData }) {
  if (!stockData || !stockData.aiReport) return null;
  const { aiReport, symbol } = stockData;

  const recommendation = aiReport.recommendation || "NEUTRAL / HOLD";
  const confidence = aiReport.marketRegime?.confidence ?? 50.0;
  const regime = aiReport.marketRegime?.regime || "SIDEWAYS";
  const volSurge = aiReport.marketRegime?.volSurge ?? 1.0;
  const rsi14 = aiReport.marketRegime?.rsi14 ?? "N/A";
  const atrPct = aiReport.marketRegime?.atrPct ?? "N/A";
  const summary = aiReport.summary || `Institutional volume analysis for ${symbol}.`;
  const keyLevels = aiReport.keyLevels || {};

  const isBullish = /BULLISH|BUY|ACCUMULATION/i.test(recommendation);
  const isBearish = /BEARISH|SELL|SHORT|DISTRIBUTION/i.test(recommendation);

  const insights = [
    { icon: <CheckCircle2 size={14} />, text: `Market Regime: ${regime} (${confidence}% confidence)` },
    { icon: <CheckCircle2 size={14} />, text: `Volume Surge vs 20-Day SMA: ${volSurge}x` },
    { icon: <CheckCircle2 size={14} />, text: `RSI(14): ${rsi14} | ATR%: ${atrPct}` },
    ...(stockData.latest?.MFI ? [{
      icon: <CheckCircle2 size={14} />,
      text: `Money Flow Index (MFI-14): ${stockData.latest.MFI} ${stockData.latest.MFI >= 80 ? '— OVERBOUGHT' : stockData.latest.MFI <= 20 ? '— OVERSOLD' : ''}`
    }] : []),
    ...(stockData.latest?.Volume_ZScore !== undefined ? [{
      icon: <CheckCircle2 size={14} />,
      text: `Volume Z-Score: ${stockData.latest.Volume_ZScore}σ ${Math.abs(stockData.latest.Volume_ZScore) >= 2 ? '(statistically significant volume spike)' : '(normal range)'}`
    }] : []),
    ...(stockData.latest?.ADL !== undefined ? [{
      icon: stockData.latest.ADL > (stockData.latest.ADL_EMA20 || 0) ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />,
      text: `Accumulation/Distribution (ADL): ${stockData.latest.ADL > (stockData.latest.ADL_EMA20 || 0) ? 'RISING — accumulation in progress' : 'FALLING — distribution pressure'}`
    }] : []),
    ...(stockData.latest?.Pocket_Pivot ? [{
      icon: <CheckCircle2 size={14} />,
      text: `Pocket Pivot ACTIVE — today's up-day volume beat all down-days in the last 10 sessions (institutional uptick)`
    }] : []),
    ...(keyLevels.support || keyLevels.resistance ? [{
      icon: <ShieldCheck size={14} />,
      text: `Key Levels — Support: ₹${keyLevels.support ?? 'N/A'} | Resistance: ₹${keyLevels.resistance ?? 'N/A'} | VWAP: ₹${keyLevels.vwap ?? 'N/A'}`
    }] : [])
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Cpu color="var(--accent-blue)" size={20} />
          AI Institutional Volume Commentary - {symbol}
        </div>
      </div>

      {/* Signal Banner */}
      <div style={{
        background: isBullish ? 'rgba(0, 245, 160, 0.1)' : isBearish ? 'rgba(255, 51, 102, 0.1)' : 'rgba(255, 215, 0, 0.1)',
        border: `1px solid ${isBullish ? 'var(--accent-green)' : isBearish ? 'var(--accent-red)' : 'var(--accent-gold)'}`,
        borderRadius: '10px',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px'
      }}>
        <div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Detected Pattern & Signal
          </span>
          <div style={{
            fontSize: '1.15rem',
            fontWeight: 700,
            color: isBullish ? 'var(--accent-green)' : isBearish ? 'var(--accent-red)' : 'var(--accent-gold)',
            marginTop: 2
          }}>
            {recommendation}
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Regime Confidence</span>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFF' }}>{confidence}%</div>
        </div>
      </div>

      {/* AI Summary */}
      <p style={{ fontSize: '0.88rem', lineHeight: '1.6', color: 'var(--text-main)', margin: '14px 0 0' }}>
        {summary}
      </p>

      {/* Key Insights List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
        <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Technical Observations:
        </span>
        {insights.map((insight, idx) => (
          <div key={idx} style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
            background: 'var(--bg-subtle)',
            padding: '12px 14px',
            borderRadius: '8px',
            fontSize: '0.88rem',
            lineHeight: '1.5'
          }}>
            <span style={{ color: 'var(--accent-green)', marginTop: 2, flexShrink: 0, display: 'inline-flex' }}>
              {insight.icon}
            </span>
            <div>{insight.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
