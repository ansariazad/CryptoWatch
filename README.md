# CryptoWatch

Real-time cryptocurrency dashboard with 50+ assets, portfolio tracking, and email price alerts.

## Features

- 📊 **Live Market Data** — Track 50+ cryptocurrencies with real-time prices
- 📈 **Interactive Charts** — 7d, 30d, 90d historical price charts via Chart.js
- 💼 **Portfolio Calculator** — Add holdings, track profit/loss in multiple currencies
- 🔔 **Price Alerts** — Set above/below triggers with email notifications
- 🔍 **Search** — Find any coin from 10,000+ supported assets
- 📱 **Responsive** — Works on desktop and mobile

## Tech Stack

- **Backend:** Python, Flask
- **API:** CoinGecko (free, no key required)
- **Charts:** Chart.js
- **Database:** SQLite
- **Alerts:** SMTP email notifications

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/markets` | Top 50 coins by market cap |
| GET | `/api/coin/<id>` | Detailed coin data |
| GET | `/api/chart/<id>?days=7` | Historical price data |
| GET/POST/DELETE | `/api/portfolio` | Portfolio CRUD |
| GET/POST/DELETE | `/api/alerts` | Price alert CRUD |
| GET | `/api/search?q=bitcoin` | Search coins |

## Setup

```bash
pip install flask requests
python app.py
# Open http://localhost:5000
```

## Author

**Azad Ansari** — [Portfolio](https://ansariazad.github.io) · [GitHub](https://github.com/ansariazad)
