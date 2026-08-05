import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

export default function AIInsights({ stockData }) {
  if (!stockData || !stockData.aiReport) return null;
  const { aiReport, symbol } = stockData;
  const { signal, confidence, volumeSurgeRatio, cmf, obvTrend, keyInsights } = aiReport;

  const isBullish = signal.includes("BULLISH") || signal.includes("ACCUMULATION");
  const isBearish = signal.includes("BEARISH") || signal.includes("DISTRIBUTION");

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
        justifyContent: 'space-between'
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
            {signal}
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence</span>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFF' }}>{confidence}</div>
        </div>
      </div>

      {/* Key Insights List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Technical Observations:
        </span>
        {keyInsights && keyInsights.map((insight, idx) => (
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
            <ArrowRight size={16} color="var(--accent-green)" style={{ marginTop: 2, flexShrink: 0 }} />
            <div dangerouslySetInnerHTML={{ __html: insight.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
          </div>
        ))}
      </div>
    </div>
  );
}
