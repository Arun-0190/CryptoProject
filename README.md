# ArbRadar — Funding Rate Arbitrage Dashboard

A real-time crypto arbitrage dashboard inspired by Coinglass, focused on identifying funding rate inefficiencies across exchanges — especially Indian platforms.

---

## Why I Built This

Most arbitrage tools like Coinglass don’t support many Indian exchanges such as Delta Exchange, CoinDCX, and CoinSwitch.

I wanted to:

* Track arbitrage opportunities for coins not available on existing platforms
* Build a clean, real-time dashboard similar to professional trading tools
* Understand how funding rate arbitrage works at a system level

---

## Features

* Real-time arbitrage opportunities
* Funding rate comparison across exchanges
* APR & profit estimation
* Long/Short strategy suggestion
* Smooth UI updates (no flickering)
* Dark trading dashboard UI
* 🇮🇳 Focus on Indian exchanges (Delta, CoinDCX, CoinSwitch)

---

## Tech Stack

### Backend

* Python (FastAPI)
* Async API calls (`httpx`)
* Arbitrage computation engine

### Frontend

* React + TypeScript
* Tailwind CSS
* Zustand (state management)

---

## How It Works

1. Fetch funding rates from Binance API
2. Simulate/compare rates across exchanges
3. Identify:

   * Long → lowest funding rate
   * Short → highest funding rate
4. Compute:

   * Funding spread
   * APR
   * Risk & confidence score

---

## Setup

### 1 Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:
http://127.0.0.1:8000

---

### 2 Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
http://localhost:5173

---

## API Endpoint

```
GET /api/arbitrage-opportunities
```

Returns:

* Symbol
* Long/Short exchanges
* Funding rate spread
* APR
* Risk & confidence

---

## Current Limitations

* Some exchanges use simulated funding rates (no public API)
* No execution engine (only analysis)
* No slippage/fees calculation yet

---

## Future Improvements

* 🔌 Real API integration for:

  * Delta Exchange
  * CoinDCX
  * CoinSwitch
* WebSocket real-time updates
* Order book + liquidity analysis
* Trade execution simulation
* Advanced charts & analytics

---

## Preview

(Add your screenshots here)

---

## Inspiration

Inspired by Coinglass Arbitrage Dashboard, but extended for broader and regional exchange coverage.

---

##  Author

Built by:
 - Arun Kumar
 - Amitabh Mathur


---

## Final Note

This project is not just a UI clone — it’s an attempt to understand and build real arbitrage systems from scratch.
