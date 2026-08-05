import React, { useState } from 'react';
import { Search, TrendingUp, Globe, Layers, Server } from 'lucide-react';

export default function Navbar({ selectedSymbol, onSelectSymbol, popularStocks, onOpenDeployModal }) {
  const [query, setQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = popularStocks.filter(
    s => s.symbol.toLowerCase().includes(query.toLowerCase()) ||
         s.name.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (sym) => {
    onSelectSymbol(sym);
    setQuery('');
    setShowDropdown(false);
  };

  return (
    <nav className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <TrendingUp size={22} />
        </div>
        <div>
          <span>VoluMetric</span>
          <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--accent-green)', fontWeight: 500 }}>
            Volume Research Terminal
          </span>
        </div>
      </div>

      <div className="search-box">
        <Search className="search-icon" size={18} />
        <input
          type="text"
          className="search-input"
          placeholder="Search Stock (e.g. RELIANCE, TCS, AAPL)..."
          value={query}
          onChange={(e) => { setQuery(e.target.value); setShowDropdown(true); }}
          onFocus={() => setShowDropdown(true)}
        />

        {showDropdown && query.length > 0 && (
          <div style={{
            position: 'absolute',
            top: '105%',
            left: 0,
            right: 0,
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            maxHeight: '260px',
            overflowY: 'auto',
            zIndex: 200
          }}>
            {filtered.length > 0 ? (
              filtered.map((stk) => (
                <div
                  key={stk.symbol}
                  onClick={() => handleSelect(stk.symbol)}
                  style={{
                    padding: '10px 14px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderBottom: '1px solid rgba(255,255,255,0.05)'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-subtle)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div>
                    <span style={{ fontWeight: 600, color: '#FFF' }}>{stk.symbol}</span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block' }}>{stk.name}</span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--accent-blue)', background: 'rgba(56,189,248,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                    {stk.exchange}
                  </span>
                </div>
              ))
            ) : (
              <div
                onClick={() => handleSelect(query)}
                style={{ padding: '12px', color: 'var(--accent-green)', cursor: 'pointer', fontSize: '0.9rem' }}
              >
                🔍 Analyze custom ticker: <strong>{query.toUpperCase()}</strong>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="nav-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <span className="live-pulse"></span> Live Stream
        </div>
        <button className="btn btn-primary" onClick={onOpenDeployModal}>
          <Globe size={16} /> Deploy & Host Live
        </button>
      </div>
    </nav>
  );
}
