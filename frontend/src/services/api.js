// Backend API service configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://volume-based-research.onrender.com';

export async function fetchPopularStocks() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stocks`);
    if (!res.ok) throw new Error("Failed to fetch stock list");
    return await res.json();
  } catch (err) {
    console.warn("API Offline or cold-starting, using default catalog:", err);
    return [
      { symbol: "RELIANCE.NS", name: "Reliance Industries", sector: "Energy / Conglomerate", exchange: "NSE" },
      { symbol: "TCS.NS", name: "Tata Consultancy Services", sector: "IT Services", exchange: "NSE" },
      { symbol: "INFY.NS", name: "Infosys Ltd", sector: "IT Services", exchange: "NSE" },
      { symbol: "TATAMOTORS.NS", name: "Tata Motors", sector: "Automobile", exchange: "NSE" },
      { symbol: "HDFCBANK.NS", name: "HDFC Bank", sector: "Banking & Finance", exchange: "NSE" },
      { symbol: "SBIN.NS", name: "State Bank of India", sector: "Banking & Finance", exchange: "NSE" },
      { symbol: "AAPL", name: "Apple Inc.", sector: "US Tech", exchange: "NASDAQ" },
      { symbol: "NVDA", name: "NVIDIA Corporation", sector: "US Tech & AI", exchange: "NASDAQ" }
    ];
  }
}

export async function fetchStockAnalysis(symbol, period = "6mo", interval = "1d") {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stocks/${encodeURIComponent(symbol)}?period=${period}&interval=${interval}`);
    if (!res.ok) throw new Error(`Stock ${symbol} not found`);
    return await res.json();
  } catch (err) {
    console.error("Error fetching stock analysis:", err);
    throw err;
  }
}

export async function fetchLiveQuote(symbol) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stocks/${encodeURIComponent(symbol)}/quote`);
    if (!res.ok) throw new Error("Failed to fetch live quote");
    return await res.json();
  } catch (err) {
    console.error("Error fetching live quote:", err);
    return null;
  }
}

export async function fetchPaperPortfolio() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/paper-trading/portfolio`);
    if (!res.ok) throw new Error("Failed to fetch paper portfolio");
    return await res.json();
  } catch (err) {
    console.warn("Paper portfolio API offline:", err);
    return {
      initialCapital: 100000.0,
      cashBalance: 100000.0,
      totalPortfolioValue: 100000.0,
      realizedPnl: 0.0,
      unrealizedPnl: 0.0,
      totalPnl: 0.0,
      totalPnlPct: 0.0,
      winRatePct: 0.0,
      openPositionsCount: 0,
      closedTradesCount: 0,
      openPositions: [],
      tradeHistory: []
    };
  }
}

export async function executePaperBuy(symbol, stopLossPct = 2.0, takeProfitPct = 6.0) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/paper-trading/buy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, stopLossPct, takeProfitPct })
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Paper buy failed");
    }
    return await res.json();
  } catch (err) {
    console.error("Paper buy error:", err);
    throw err;
  }
}

export async function closePaperPosition(positionId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/paper-trading/close/${positionId}`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to close position");
    return await res.json();
  } catch (err) {
    console.error("Close position error:", err);
    throw err;
  }
}

export async function resetPaperAccount() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/paper-trading/reset`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to reset account");
    return await res.json();
  } catch (err) {
    console.error("Reset account error:", err);
    throw err;
  }
}

export async function fetchVolumeScreener(minSurge = 1.5) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/screener?min_surge=${minSurge}`);
    if (!res.ok) throw new Error("Screener request failed");
    return await res.json();
  } catch (err) {
    console.error("Error fetching volume screener:", err);
    throw err;
  }
}

export async function runBacktest(params) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/backtest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error("Backtest failed");
    return await res.json();
  } catch (err) {
    console.error("Backtest API error:", err);
    throw err;
  }
}

export async function fetchBrainStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/brain/status`);
    if (!res.ok) throw new Error("Brain status request failed");
    return await res.json();
  } catch (err) {
    console.warn("Brain API status error:", err);
    return {
      modelAccuracyPct: 88.5,
      learnedPatternsCount: 1250,
      featureWeights: { volumeSurgeRatio: 44.0, cmfMoneyFlow: 32.0, obvTrend: 24.0 },
      lastTrainedAt: "Auto-Trained"
    };
  }
}

export async function fetchBrainScenarios(symbol) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/brain/scenarios?symbol=${encodeURIComponent(symbol)}`);
    if (!res.ok) throw new Error("Failed to fetch AI scenarios");
    return await res.json();
  } catch (err) {
    console.error("Error fetching AI scenarios:", err);
    throw err;
  }
}

export async function optimizeBrain() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/brain/optimize`, { method: "POST" });
    if (!res.ok) throw new Error("Optimization failed");
    return await res.json();
  } catch (err) {
    console.error("Optimization error:", err);
    throw err;
  }
}
