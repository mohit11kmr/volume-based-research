import React from 'react';
import { Layers, Target } from 'lucide-react';

export default function VolumeProfile({ stockData }) {
  if (!stockData || !stockData.volumeProfile) return null;
  const { volumeProfile, symbol } = stockData;

  const maxVol = Math.max(...volumeProfile.map(p => p.volume || 0), 1);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Layers color="var(--accent-gold)" size={20} />
          Volume Profile & Point of Control (POC)
        </div>
      </div>

      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
        Horizontal volume distribution across price levels for <strong>{symbol}</strong>. High volume nodes (POC) represent institutional consolidation zones.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '6px' }}>
        {volumeProfile.map((bin, index) => {
          const volValue = bin.volume || 0;
          const fillWidthPct = Math.round((volValue / maxVol) * 100);

          return (
            <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>
                <span style={{ color: bin.isPOC ? 'var(--accent-gold)' : 'var(--text-main)', fontWeight: bin.isPOC ? 700 : 400 }}>
                  {bin.isPOC && <Target size={12} inline style={{ marginRight: 4 }} />}
                  ₹{bin.priceRange}
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {(volValue / 1000).toFixed(0)}k shares
                </span>
              </div>

              <div style={{
                background: 'rgba(255,255,255,0.05)',
                borderRadius: '4px',
                height: '14px',
                width: '100%',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <div style={{
                  width: `${fillWidthPct}%`,
                  height: '100%',
                  background: bin.isPOC
                    ? 'linear-gradient(90deg, #FFD700, #FFA500)'
                    : 'linear-gradient(90deg, #00F5A0, #38BDF8)',
                  borderRadius: '4px',
                  transition: 'width 0.4s ease'
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
