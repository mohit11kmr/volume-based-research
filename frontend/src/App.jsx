import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MarketSummary from './components/MarketSummary';
import StockChart from './components/StockChart';
import VolumeProfile from './components/VolumeProfile';
import VolumeScreener from './components/VolumeScreener';
import Backtesting from './components/Backtesting';
import AIInsights from './components/AIInsights';
import BrainDashboard from './components/BrainDashboard';
import PaperTrading from './components/PaperTrading';
import HostingGuideModal from './components/HostingGuideModal';
import { fetchPopularStocks, fetchStockAnalysis } from './services/api';
import { BarChart3, Filter, Play, Cpu, AlertCircle, Sparkles, DollarSign } from 'lucide-react';

export default function App() {
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS');
  const [popularStocks, setPopularStocks] = useState([]);
  const [stockData, setStockData] = useState(null);
  const [period, setPeriod] = useState('6mo');
  const [interval, setInterval] = useState('1d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isDeployModalOpen, setIsDeployModalOpen] = useState(false);
  const [appliedStrategy, setAppliedStrategy] = useState(null);

  useEffect(() => {
    async function loadCatalog() {
      const stocks = await fetchPopularStocks();
      setPopularStocks(stocks);
    }
    loadCatalog();
  }, []);

  useEffect(() => {
    async function loadStockDetails() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchStockAnalysis(selectedSymbol, period, interval);
        setStockData(data);
      } catch (err) {
        setError(`Failed to fetch stock data for ${selectedSymbol}.`);
      } finally {
        setLoading(false);
      }
    }
    loadStockDetails();
  }, [selectedSymbol, period, interval]);

  const handleTimeframeChange = (newPeriod, newInterval) => {
    setPeriod(newPeriod);
    setInterval(newInterval);
  };

  const handleApplyStrategy = (strategy) => {
    setAppliedStrategy(strategy);
    setActiveTab('backtest');
  };

  return (
    <div className="app-container">
      <Navbar
        selectedSymbol={selectedSymbol}
        onSelectSymbol={setSelectedSymbol}
        popularStocks={popularStocks}
        onOpenDeployModal={() => setIsDeployModalOpen(true)}
      />

      <main className="main-content">
        <MarketSummary
          stockData={stockData}
          popularStocks={popularStocks}
          onSelectSymbol={setSelectedSymbol}
        />

        <div className="tabs-header">
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <BarChart3 size={18} /> Volume Analytics & Chart
          </button>
          <button
            className={`tab-btn ${activeTab === 'screener' ? 'active' : ''}`}
            onClick={() => setActiveTab('screener')}
          >
            <Filter size={18} /> Volume Surge Screener
          </button>
          <button
            className={`tab-btn ${activeTab === 'brain' ? 'active' : ''}`}
            onClick={() => setActiveTab('brain')}
          >
            <Sparkles size={18} color="var(--accent-gold)" /> AI Self-Learning Brain & Zero-Loss Finder
          </button>
          <button
            className={`tab-btn ${activeTab === 'paper' ? 'active' : ''}`}
            onClick={() => setActiveTab('paper')}
          >
            <DollarSign size={18} color="var(--accent-green)" /> Paper Trading & Risk Simulator
          </button>
          <button
            className={`tab-btn ${activeTab === 'backtest' ? 'active' : ''}`}
            onClick={() => setActiveTab('backtest')}
          >
            <Play size={18} /> Strategy Backtester
          </button>
        </div>

        {/* Tab 1: Dashboard */}
        {activeTab === 'dashboard' && (
          loading ? (
            <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading Volume Analytics & Technical Indicators for {selectedSymbol}...
            </div>
          ) : error ? (
            <div style={{ padding: '24px', background: 'rgba(255,51,102,0.1)', border: '1px solid var(--accent-red)', borderRadius: '12px', color: 'var(--accent-red)', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <AlertCircle size={24} /> {error}
            </div>
          ) : (
            <div className="grid-2col">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <StockChart
                  stockData={stockData}
                  selectedPeriod={period}
                  selectedInterval={interval}
                  onTimeframeChange={handleTimeframeChange}
                />
                <AIInsights stockData={stockData} />
              </div>
              <div>
                <VolumeProfile stockData={stockData} />
              </div>
            </div>
          )
        )}

        {/* Tab 2: Screener */}
        {activeTab === 'screener' && (
          <VolumeScreener onSelectSymbol={(sym) => { setSelectedSymbol(sym); setActiveTab('dashboard'); }} />
        )}

        {/* Tab 3: AI Self-Learning Brain */}
        {activeTab === 'brain' && (
          <BrainDashboard selectedSymbol={selectedSymbol} onApplyStrategy={handleApplyStrategy} />
        )}

        {/* Tab 4: Paper Trading */}
        {activeTab === 'paper' && (
          <PaperTrading selectedSymbol={selectedSymbol} />
        )}

        {/* Tab 5: Backtest */}
        {activeTab === 'backtest' && (
          <Backtesting selectedSymbol={selectedSymbol} initialStrategy={appliedStrategy} />
        )}
      </main>

      <HostingGuideModal
        isOpen={isDeployModalOpen}
        onClose={() => setIsDeployModalOpen(false)}
      />
    </div>
  );
}
