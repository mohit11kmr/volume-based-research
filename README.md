# 📈 VoluMetric - Volume Based Share Market Research & Screener Platform

An enterprise-grade, full-stack **Volume-Based Stock Research, Screening & Strategy Backtesting Engine** designed for Indian (NSE/BSE) and Global (US Tech) equity markets.

---

## 🌟 Key Features

1. **Volume Surge & Institutional Accumulation Screener**:
   - Detects unusual volume spikes (&ge;1.5x, 2.0x, 3.0x, 5.0x 20-day SMA Volume).
   - Identifies institutional accumulation vs distribution signals.

2. **Advanced Technical Volume Indicators**:
   - **OBV (On-Balance Volume)** & 20-day OBV EMA.
   - **VWAP (Volume Weighted Average Price)** overlay.
   - **CMF (Chaikin Money Flow)** 20-period index.
   - **Volume Rate of Change (VROC)** & 20-day SMA Volume lines.

3. **Price-Wise Volume Profile & Point of Control (POC)**:
   - Horizontal volume distribution showing price levels with maximum institutional trading activity.

4. **Strategy Backtester**:
   - Backtests volume breakout strategies with custom Stop-Loss, Take-Profit, and Holding Period parameters.
   - Returns Win Rate %, Total Return %, Max Drawdown %, and Portfolio Equity Growth Curve.

5. **AI Institutional Volume Commentary**:
   - Algorithmic analysis summarizing buying vs selling pressure and market sentiment.

---

## 🏗 Technology Stack

- **Backend**: Python FastAPI, Uvicorn, Pandas, NumPy, yfinance.
- **Frontend**: React, Vite, Recharts, Lucide Icons, Custom Dark Theme Terminal CSS.
- **CI/CD & Deployment**: GitHub Actions (`.github/workflows/ci-cd.yml`), Docker, Render (Backend), Vercel (Frontend).

---

## 🔄 CI/CD & Git Workflow

This repository includes a full GitHub Actions CI/CD Pipeline located at [`.github/workflows/ci-cd.yml`](file:///.github/workflows/ci-cd.yml).

### Quick Git Commands:

```bash
# 1. Initialize Git repository
git init

# 2. Add all files & commit
git add .
git commit -m "feat: initial commit of Volume-Based Research & Screener Platform"

# 3. Connect to your GitHub repository
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/volume-based-research.git

# 4. Push to GitHub (Triggers CI/CD Pipeline automatically!)
git push -u origin main
```

---

## 🚀 How to Run Locally

### 1. Backend Setup:
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend API running at: `http://localhost:8000` (API Docs: `http://localhost:8000/docs`)

### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
Frontend web application accessible at: `http://localhost:3000`

---

## 🌐 Live Cloud Hosting Instructions (फ्री होस्टिंग निर्देश)

### Step 1: Host Backend on Render (Free Python Hosting)
1. Push code repository to GitHub.
2. Go to [Render.com](https://render.com) -> **New Web Service**.
3. Set **Root Directory**: `backend`
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Copy your Render Deploy Hook URL into your GitHub Repository Secrets as `RENDER_DEPLOY_HOOK_URL`.

### Step 2: Host Frontend on Vercel (Free React Hosting)
1. Go to [Vercel.com](https://vercel.com) -> **Add New Project**.
2. Select the `frontend` directory.
3. Add Environment Variable:
   - Name: `VITE_API_URL`
   - Value: `https://volume-based-research.onrender.com` (Your Render backend URL)
4. Click **Deploy**. Your professional trading terminal is live on the internet!
