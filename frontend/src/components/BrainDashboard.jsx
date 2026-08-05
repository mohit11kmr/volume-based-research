import React, { useState, useEffect } from 'react';
import { Cpu, ShieldCheck, Zap, RefreshCw, Award, CheckCircle2, TrendingUp, Sparkles } from 'lucide-react';
import { fetchBrainStatus, fetchBrainScenarios, optimizeBrain } from '../services/api';

export default function BrainDashboard({ selectedSymbol, onApplyStrategy }) {
  const [brainStatus, setBrainStatus] = useState(null);
  const [scenariosData, setScenariosData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [status, scenarios] = await Promise.all([
        fetchBrainStatus(),
        fetchBrainScenarios(selectedSymbol)
      ]);
      setBrainStatus(status);
      setScenariosData(scenarios);
    } catch (err) {
      setError("Connecting to Self-Learning Brain...");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSymbol]);

  const handleRetrain = async () => {
    setOptimizing(true);
    try {
      await optimizeBrain();
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* AI Brain Performance Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #121826 0%, #1A2338 100%)', border: '1px solid var(--border-active)' }}>
        <div className="card-header">
          <div className="card-title" style={{ fontSize: '1.2rem' }}>
            <Cpu color="var(--accent-green)" size={24} />
            Self-Learning AI Brain - Adaptive Model Overview
          </div>
          <button className="btn btn-primary" onClick={handleRetrain} disabled={optimizing}>
            <RefreshCw size={16} className={optimizing ? "spin" : ""} />
            {optimizing ? "Retraining ML Brain..." : "Re-Optimize Scenarios"}
          </button>
        </div>

        {brainStatus && (
          <div className="metrics-row" style={{ marginTop: '8px' }}>
            <div className="metric-card" style={{ background: 'rgba(0, 245, 160, 0.05)', borderColor: 'rgba(0, 245, 160, 0.2)' }}>
              <div className="metric-title">Model Learning Accuracy</div>
              <div className="metric-value text-green">{brainStatus.modelAccuracyPct}%</div>
              <div className="metric-sub text-green">
                <CheckCircle2 size={14} /> Machine Learning Precision
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Learned Pattern Memory</div>
              <div className="metric-value text-gold">{brainStatus.learnedPatternsCount?.toLocaleString()}</div>
              <div className="metric-sub" style={{ color: 'var(--text-muted)' }}>Historical trade instances</div>
            </div>

            <div className="metric-card" style={{ gridColumn: 'span 2' }}>
              <div className="metric-title">Learned Feature Weights</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                  <span>Volume Surge Multiple: <strong>{brainStatus.featureWeights?.volumeSurgeRatio}%</strong></span>
                  <span>Money Flow (CMF): <strong>{brainStatus.featureWeights?.cmfMoneyFlow}%</strong></span>
                  <span>OBV Trend: <strong>{brainStatus.featureWeights?.obvTrend}%</strong></span>
                </div>
                <div style={{ height: '8px', width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', display: 'flex', overflow: 'hidden' }}>
                  <div style={{ width: `${brainStatus.featureWeights?.volumeSurgeRatio}%`, background: 'var(--accent-green)' }} />
                  <div style={{ width: `${brainStatus.featureWeights?.cmfMoneyFlow}%`, background: 'var(--accent-blue)' }} />
                  <div style={{ width: `${brainStatus.featureWeights?.obvTrend}%`, background: 'var(--accent-purple)' }} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Zero-Loss Strategy Finder Section */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <ShieldCheck color="var(--accent-gold)" size={22} />
            Zero-Loss & High Probability AI Scenarios ({selectedSymbol})
          </div>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
          The AI Brain generated and evaluated <strong>60+ strategy scenarios</strong> on historical data for <strong>{selectedSymbol}</strong>. 
          Below are the lowest-risk parameter combinations optimized for zero/minimal losses.
        </p>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Evaluating 60+ Strategy Scenarios with AI Engine...
          </div>
        ) : scenariosData && scenariosData.zeroLossScenarios ? (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank & Scenario Name</th>
                  <th>Surge Multiple</th>
                  <th>Stop Loss</th>
                  <th>Take Profit</th>
                  <th>Holding Period</th>
                  <th>Win Rate %</th>
                  <th>Loss Count</th>
                  <th>Total Return</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {scenariosData.zeroLossScenarios.map((scn, idx) => (
                  <tr key={scn.scenarioId} style={{ background: scn.isZeroLoss ? 'rgba(255, 215, 0, 0.05)' : 'transparent' }}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ color: 'var(--accent-gold)', fontWeight: 700 }}>#{idx + 1}</span>
                        <strong style={{ color: '#FFF' }}>{scn.name}</strong>
                        {scn.isZeroLoss && (
                          <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                            <Sparkles size={12} /> ZERO LOSS
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ color: 'var(--accent-green)', fontWeight: 600 }}>{scn.volumeMultiplier}x</td>
                    <td className="text-red">-{scn.stopLossPct}%</td>
                    <td className="text-green">+{scn.takeProfitPct}%</td>
                    <td>{scn.holdingDays} Days</td>
                    <td className="text-green" style={{ fontWeight: 700 }}>{scn.winRatePct}%</td>
                    <td>
                      <span className={scn.losingTrades === 0 ? "badge badge-success" : "badge badge-warning"}>
                        {scn.losingTrades} Losses
                      </span>
                    </td>
                    <td className={scn.totalReturnPct >= 0 ? "text-green" : "text-red"} style={{ fontWeight: 700 }}>
                      +{scn.totalReturnPct}%
                    </td>
                    <td>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                        onClick={() => onApplyStrategy(scn)}
                      >
                        1-Click Apply Strategy
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: '20px', color: 'var(--text-muted)' }}>No scenario data available.</div>
        )}
      </div>
    </div>
  );
}
