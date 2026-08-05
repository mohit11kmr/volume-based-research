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

export async function fetchStockAnalysis(symbol, period = "6m") {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stocks/${encodeURIComponent(symbol)}?period=${period}`);
    if (!res.ok) throw new Error(`Stock ${symbol} not found`);
    return await res.json();
  } catch (err) {
    console.error("Error fetching stock analysis:", err);
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
